# Push to GitHub - Instructions

## Option 1: If you already have a GitHub repository

```bash
cd /Users/tylerhughes/Projects/SmartPlantAssistant

# Add remote (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Or if using SSH:
git remote add origin git@github.com:YOUR_USERNAME/REPO_NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Option 2: Create a new GitHub repository

1. Go to https://github.com/new
2. Create a new repository (don't initialize with README)
3. Copy the repository URL
4. Run these commands:

```bash
cd /Users/tylerhughes/Projects/SmartPlantAssistant

# Add remote (replace with your actual repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## What's included/excluded

✅ **Included**:
- All source code (backend, frontend)
- Configuration files
- README and documentation
- Tests
- `.env.example` (template for environment variables)

❌ **Excluded** (via .gitignore):
- `.env` files (contains API keys - keep secret!)
- Database files (`*.db`, `*.sqlite`)
- `node_modules/`
- Python virtual environments (`venv/`, `env/`)
- Log files

## Important Notes

1. **Never commit `.env` files** - they contain your API keys!
2. **Share `.env.example`** - shows what variables are needed without secrets
3. **Database is excluded** - users will need to run `init_db()` or create their own
4. **Update README** - make sure it has setup instructions

## If you need to add a remote

```bash
# Check current remotes
git remote -v

# If none exist, add one:
git remote add origin YOUR_GITHUB_REPO_URL
```



