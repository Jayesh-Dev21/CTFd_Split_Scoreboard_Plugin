# CTFd Split Scoreboard Plugin

This plugin for CTFd allows splitting the main scoreboard into separate views based on specific criteria, such as team attributes or user email domains.

**Note:** This plugin currently only supports CTFd's 'Teams' mode.

## Features

- **Split by Team Attributes:** Create separate leaderboards for teams that match a specific custom field value (e.g., "Beginner" vs. "Advanced").
- **Split by Team Size:** Isolate teams based on the number of members (e.g., teams with exactly 3 members).
- **Split by Email Domain:** Create a dedicated scoreboard for users from a particular organization or university (e.g., `...@your-university.edu`).
- **Custom Scoreboard:** An optional tab allowing users to select specific teams they want to follow and compare.

## Installation

1.  Clone this repository into your CTFd `plugins` directory:
    ```sh
    git clone https://github.com/Jayesh-Dev21/CTFd_Split_Scoreboard.git
    ```
2.  Restart your CTFd instance.

## Usage

1.  Navigate to the CTFd Admin Panel.
2.  Go to **Plugins > Split Scoreboard**.
3.  From the "Split Based on" dropdown, select the criterion for the split.
4.  Enter the value to match in the "Matching Value" field.
5.  Customize the titles for the "Matched" and "Unmatched" scoreboard tabs (if applicable).
6.  Optionally, enable the "Allow custom scoreboard" feature.
7.  Click **Submit**.

The main scoreboard will now display separate tabs based on your configuration.

### Example: Splitting by Email Domain

Let's say you want to create a separate leaderboard for students from "iitbhu.ac.in" and another for everyone else.

1.  **Split Based on:** Select `Email Domain`.
2.  **Where value matches:** Enter `iitbhu.ac.in`.
3.  The "Matching Title" and "Unmatching Title" fields will be hidden as they are not needed for this option. The titles will default to "iitbhu.ac.in" and "Other".
4.  Click **Submit**.

Now, the scoreboard will have two tabs:
-   **iitbhu.ac.in:** Shows only participants with an `@iitbhu.ac.in` email address.
-   **Other:** Shows all other participants.

### Other Split Options

*   **Team Attributes:** Choose a custom team field (e.g., "Country"). You can create custom fields under **Admin Panel > Config > Custom Fields**.
    *   **Where value matches:** Enter the value you want to match (e.g., "USA").
    *   **Matching Title:** `USA Teams`
    *   **Unmatching Title:** `International Teams`
*   **Team Size:** Options to filter by exact, less than, or greater than a specified number.
    *   **Where value matches:** Enter the number of members (e.g., `3`).
    *   **Matching Title:** `Teams of 3`
    *   **Unmatching Title:** `Other Teams`

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

[Apache License 2.0](https://choosealicense.com/licenses/apache-2.0/)


---

Original - https://github.com/durkinza/CTFd_Split_Scoreboard.git

---