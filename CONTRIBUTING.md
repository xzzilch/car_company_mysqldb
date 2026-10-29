# Contributing

Thanks for helping improve this school project. Keep changes small, readable, and consistent with the existing Python and documentation style.

## Before opening a change

1. Create a branch for your change.
2. Make the smallest change that addresses the issue.
3. Run the automated tests from the project folder:

   ```sh
   python -m unittest discover -s tests
   ```

4. Check the formatting of edited Markdown and confirm its links point to existing files.
5. Describe what changed and how you tested it in your pull request.

The automated tests use fake database objects and do not need MySQL. For changes to database behavior, also test against a disposable MySQL database when possible.

## Reporting a problem

Use the [bug report form](.github/ISSUE_TEMPLATE/bug_report.yml) for problems
or the [feature request form](.github/ISSUE_TEMPLATE/feature_request.yml) for
ideas. Include the steps or use case, expected behavior, and relevant operating
system/Python details. Never include a MySQL password, private connection
details, or real personal data in an issue or pull request.

Pull requests use the checklist in
[.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md).
