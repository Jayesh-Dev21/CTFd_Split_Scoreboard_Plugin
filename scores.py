from sqlalchemy.sql.expression import union_all
from sqlalchemy import func

from CTFd.cache import cache
from CTFd.models import db, Teams, Users, Solves, Awards, Challenges, TeamFieldEntries, Fields
from CTFd.utils.dates import unix_time_to_utc
from CTFd.utils import get_config
from CTFd.utils.modes import get_model

@cache.memoize(timeout=60)
def get_scores(admin=False):
    """
    Get scores for all users.
    If admin is True, include hidden and banned users.
    """
    Model = get_model()
    scores = (
        db.session.query(
            Solves.account_id.label("account_id"),
            func.sum(Challenges.value).label("score"),
        )
        .join(Challenges)
        .group_by(Solves.account_id)
    )

    awards = (
        db.session.query(
            Awards.account_id.label("account_id"),
            func.sum(Awards.value).label("score"),
        )
        .group_by(Awards.account_id)
    )

    if admin:
        freeze = get_config("freeze")
        if freeze:
            scores = scores.filter(Solves.date < unix_time_to_utc(freeze))
            awards = awards.filter(Awards.date < unix_time_to_utc(freeze))

    else:
        freeze = get_config("freeze")
        if freeze:
            scores = scores.filter(Solves.date < unix_time_to_utc(freeze))
            awards = awards.filter(Awards.date < unix_time_to_utc(freeze))

        if get_config("user_mode") == "teams":
            scores = scores.join(Teams, Solves.account_id == Teams.id).filter(
                Teams.banned == False, Teams.hidden == False
            )
            awards = awards.join(Teams, Awards.account_id == Teams.id).filter(
                Teams.banned == False, Teams.hidden == False
            )
        else:
            scores = scores.join(Users, Solves.account_id == Users.id).filter(
                Users.banned == False, Users.hidden == False
            )
            awards = awards.join(Users, Awards.account_id == Users.id).filter(
                Users.banned == False, Users.hidden == False
            )

    results = union_all(scores, awards).alias("results")

    sumscores = (
        db.session.query(
            results.columns.account_id,
            func.sum(results.columns.score).label("score"),
        )
        .group_by(results.columns.account_id)
        .subquery()
    )
    
    if get_config("user_mode") == "teams":
        sumscores_cte = (
            db.session.query(
                Model.id.label("account_id"),
                func.coalesce(sumscores.columns.score, 0).label("score"),
            )
            .outerjoin(sumscores, Model.id == sumscores.columns.account_id)
            .subquery()
        )
    else: # Users mode
        sumscores_cte = (
            db.session.query(
                Model.id.label("account_id"),
                func.coalesce(sumscores.columns.score, 0).label("score"),
            )
            .outerjoin(sumscores, Model.id == sumscores.columns.account_id)
            .subquery()
        )
    return sumscores_cte

@cache.memoize(timeout=60)
def get_team_ids():
    attr_id = get_config("split_scoreboard_attr", 0)
    attr_value = get_config("split_scoreboard_value", "hidden")

    team_ids = []
    if attr_id == "-1": # Where team size is <value>
        teams = Teams.query.outerjoin(Teams.members).group_by(Teams).having(func.count_(Teams.members) == attr_value)
        for team in teams:
            team_ids.append(team.id)
    elif attr_id == "-2": # Where team size is less than <value> 
        teams = Teams.query.outerjoin(Teams.members).group_by(Teams).having(func.count_(Teams.members) <= attr_value)
        for team in teams:
            team_ids.append(team.id)
    elif attr_id == "-3": # Where team size is greater than <value> 
        teams = Teams.query.outerjoin(Teams.members).group_by(Teams).having(func.count_(Teams.members) >= attr_value)
        for team in teams:
            team_ids.append(team.id)
    elif attr_id == "-4": # Where user email ends with
        users = Users.query.filter(Users.email.like(f"%{attr_value}"))
        user_ids = [user.id for user in users]
        if get_config("user_mode") == "teams":
            # If in teams mode, we need to get the team IDs for these users
            teams = Teams.query.join(Users, Teams.members).filter(Users.id.in_(user_ids)).all()
            team_ids = [team.id for team in teams]
        else:
            # In users mode, the user IDs are the account IDs
            team_ids = user_ids
    else:
        teams = TeamFieldEntries.query.filter_by(
            field_id = attr_id
        ).filter(
            func.lower(TeamFieldEntries.value) == func.lower(str(attr_value))
        )
        for team in teams:
            team_ids.append(team.team_id)

    return team_ids


@cache.memoize(timeout=60)
def get_unmatched_standings(count=None, admin=False, fields=[]):
    """
    Get standings as a list of tuples containing account_id, name, and score e.g. [(account_id, team_name, score)].
    """
    if fields is None:
        fields = []
    
    Model = get_model()

    team_ids = get_team_ids()
    sumscores = get_scores(admin)

    """
    Admins can see scores for all users but the public cannot see banned users.
    Filters out banned users.
    Properly resolves value ties by ID.
    """
    if admin:
        standings_query = (
            db.session.query(
                Model.id.label("account_id"),
                Model.oauth_id.label("oauth_id"),
                Model.name.label("name"),
                Model.hidden,
                Model.banned,
                sumscores.columns.score,
                *fields,
            )
            .join(sumscores, Model.id == sumscores.columns.account_id)
			.filter(Model.id.notin_(team_ids))
            .order_by(sumscores.columns.score.desc(), Model.id)
        )
    else:
        standings_query = (
            db.session.query(
                Model.id.label("account_id"),
                Model.oauth_id.label("oauth_id"),
                Model.name.label("name"),
                sumscores.columns.score,
                *fields,
            )
            .join(sumscores, Model.id == sumscores.columns.account_id)
            .filter(Model.banned == False, Model.hidden == False)
			.filter(Model.id.notin_(team_ids))
            .order_by(sumscores.columns.score.desc(), Model.id)
        )

    """
    Only select a certain amount of users if asked.
    """
    if count is None:
        standings = standings_query.all()
    else:
        standings = standings_query.limit(count).all()

    return standings

@cache.memoize(timeout=60)
def get_custom_standings(count=None, admin=False, team_ids=[], fields=[]):

    if fields is None:
        fields = []
    Model = get_model()
    sumscores = get_scores(admin)

    """
    Admins can see scores for all users but the public cannot see banned users.
    """
    if admin:
        standings_query = (
            db.session.query(
                Model.id.label("account_id"),
                Model.oauth_id.label("oauth_id"),
                Model.name.label("name"),
                Model.hidden,
                Model.banned,
                sumscores.columns.score,
                *fields,
            )
            .join(sumscores, Model.id == sumscores.columns.account_id)
			.filter(Model.id.in_(team_ids))
            .order_by(sumscores.columns.score.desc(), Model.id)
        )
    else:
        standings_query = (
            db.session.query(
                Model.id.label("account_id"),
                Model.oauth_id.label("oauth_id"),
                Model.name.label("name"),
                sumscores.columns.score,
                *fields,
            )
            .join(sumscores, Model.id == sumscores.columns.account_id)
            .filter(Model.banned == False, Model.hidden == False)
			.filter(Model.id.in_(team_ids))
            .order_by(sumscores.columns.score.desc(), Model.id)
        )

    """
    Only select a certain amount of users if asked.
    """
    if count is None:
        standings = standings_query.all()
    else:
        standings = standings_query.limit(count).all()

    return standings


@cache.memoize(timeout=60)
def get_matched_standings(count=None, admin=False, fields=None):
    
    if fields is None:
        fields = []

    attr_id = get_config("split_scoreboard_attr")
    # If splitting by email, we must use the Users model, even in teams mode.
    if str(attr_id) == "-4":
        Model = Users
        sumscores = get_scores_for_users(admin)
    else:
        Model = get_model()
        sumscores = get_scores(admin)


    team_ids = get_team_ids()

    """
    Admins can see scores for all users but the public cannot see banned users.
    """
    if admin:
        standings_query = (
            db.session.query(
                Model.id.label("account_id"),
                Model.oauth_id.label("oauth_id"),
                Model.name.label("name"),
                Model.hidden,
                Model.banned,
                sumscores.columns.score,
                *fields,
            )
            .join(sumscores, Model.id == sumscores.columns.account_id)
			.filter(Model.id.in_(team_ids))
            .order_by(sumscores.columns.score.desc(), Model.id)
        )
    else:
        standings_query = (
            db.session.query(
                Model.id.label("account_id"),
                Model.oauth_id.label("oauth_id"),
                Model.name.label("name"),
                sumscores.columns.score,
                *fields,
            )
            .join(sumscores, Model.id == sumscores.columns.account_id)
            .filter(Model.banned == False, Model.hidden == False)
			.filter(Model.id.in_(team_ids))
            .order_by(sumscores.columns.score.desc(), Model.id)
        )

    """
    Only select a certain amount of users if asked.
    """
    if count is None:
        standings = standings_query.all()
    else:
        standings = standings_query.limit(count).all()

    return standings

def get_scores_for_users(admin=False):
    """
    Get scores for all users, regardless of team mode.
    """
    scores = (
        db.session.query(
            Solves.user_id.label("account_id"),
            func.sum(Challenges.value).label("score"),
        )
        .join(Challenges)
        .group_by(Solves.user_id)
    )

    awards = (
        db.session.query(
            Awards.user_id.label("account_id"),
            func.sum(Awards.value).label("score"),
        )
        .group_by(Awards.user_id)
    )

    if admin:
        freeze = get_config("freeze")
        if freeze:
            scores = scores.filter(Solves.date < unix_time_to_utc(freeze))
            awards = awards.filter(Awards.date < unix_time_to_utc(freeze))
    else:
        freeze = get_config("freeze")
        if freeze:
            scores = scores.filter(Solves.date < unix_time_to_utc(freeze))
            awards = awards.filter(Awards.date < unix_time_to_utc(freeze))
        
        scores = scores.join(Users, Solves.user_id == Users.id).filter(
            Users.banned == False, Users.hidden == False
        )
        awards = awards.join(Users, Awards.user_id == Users.id).filter(
            Users.banned == False, Users.hidden == False
        )

    results = union_all(scores, awards).alias("results")

    sumscores = (
        db.session.query(
            results.columns.account_id,
            func.sum(results.columns.score).label("score"),
        )
        .group_by(results.columns.account_id)
        .subquery()
    )

    sumscores_cte = (
        db.session.query(
            Users.id.label("account_id"),
            func.coalesce(sumscores.columns.score, 0).label("score"),
        )
        .outerjoin(sumscores, Users.id == sumscores.columns.account_id)
        .subquery()
    )
    return sumscores_cte
    if admin:
        standings_query = (
            db.session.query(
                Model.id.label("account_id"),
                Model.oauth_id.label("oauth_id"),
                Model.name.label("name"),
                Model.hidden,
                Model.banned,
                sumscores.columns.score,
                *fields,
            )
            .join(sumscores, Model.id == sumscores.columns.account_id)
			.filter(Model.id.in_(team_ids))
            .order_by(sumscores.columns.score.desc(), sumscores.columns.id)
        )
    else:
        standings_query = (
            db.session.query(
                Model.id.label("account_id"),
                Model.oauth_id.label("oauth_id"),
                Model.name.label("name"),
                sumscores.columns.score,
                *fields,
            )
            .join(sumscores, Model.id == sumscores.columns.account_id)
            .filter(Model.banned == False, Model.hidden == False)
			.filter(Model.id.in_(team_ids))
            .order_by(sumscores.columns.score.desc(), sumscores.columns.id)
        )

    """
    Only select a certain amount of users if asked.
    """
    if count is None:
        standings = standings_query.all()
    else:
        standings = standings_query.limit(count).all()

    return standings

