# Git preparation and publication

Inspect the current branch, commits, and remotes before publishing. The initial
architecture setup did not create a commit or remote automatically; later user
changes may already have configured them. Publication requires the chosen repository
and authorized access.

```powershell
git status --short
git remote -v
git add <reviewed-paths>
git diff --cached --stat
git diff --cached
git commit -m "chore: bootstrap Cosmic Hunter AI architecture"
# Only if origin has not been configured:
git remote add origin https://github.com/ORGANIZATION/cosmic-hunter-ai.git
git push -u origin main
```

Replace ORGANIZATION and confirm the repository name before running these examples.
Replace `<reviewed-paths>` with the files intended for the commit. Example credentials
in .env.example are for local development only. Review the staged diff before committing;
.gitignore does not remove previously tracked secrets. Rotate exposed keys even if
later removed from history. Keep FITS files/models outside Git; store manifests with
references, checksums, and access conditions.

The GitHub Actions CI workflow was removed at the team's request. Run the local
verification commands in README.md before sharing changes.
Configure main branch protection and pull request reviews in GitHub. Verify the SQL
schema against real PostgreSQL; generating the file is not sufficient.
