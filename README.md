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
3.  From the "Split Based on" dropdown, select the criterion for the split:
    *   **Team Attributes:** Choose a custom team field. You can create custom fields under **Admin Panel > Config > Custom Fields**.
    *   **Team Size:** Options to filter by exact, less than, or greater than a specified number.
    *   **Email Domain:** To filter users by their email address ending (e.g., `gmail.com`).
4.  Enter the value to match in the "Matching Value" field.
5.  Customize the titles for the "Matched" and "Unmatched" scoreboard tabs.
6.  Optionally, enable the "Allow custom scoreboard" feature.
7.  Click **Submit**.

The main scoreboard will now display separate tabs based on your configuration.

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

[Apache License 2.0](https://choosealicense.com/licenses/apache-2.0/)


---

Original - https://github.com/durkinza/CTFd_Split_Scoreboard.git

---