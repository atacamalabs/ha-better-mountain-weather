# GitHub Setup Guide

## If You Don't Have a GitHub Account Yet

### 1. Create GitHub Account

1. Go to https://github.com/signup
2. Enter your email address
3. Create a password
4. Choose a username (this will be in your URLs)
5. Verify your email
6. Complete the setup

**Username Tips:**
- Use lowercase letters, numbers, hyphens
- Make it professional (it'll be in your integration URL)
- Examples: `mountain-weather`, `your-name`, `alpine-dev`

---

## If You Already Have a GitHub Account

Great! Just provide your username and we'll configure everything.

---

## What I'll Do Once You Provide Your Info

1. **Configure Git locally** with your name and email
2. **Update all files** with your GitHub username
3. **Create a GitHub repository** (I'll guide you through the web interface)
4. **Push your code** to GitHub
5. **Create the first release** (v0.1.0b1)
6. **Set up HACS** compatibility

---

## Information Needed

Please provide:

```
GitHub username: _______________
Your name: _______________
Email: _______________
```

Once you provide this, I'll:
- Configure Git
- Update manifest.json
- Update README.md
- Create a setup script
- Guide you through creating the repo

---

## Alternative: Manual Setup

If you prefer to do it manually, follow these steps:

### 1. Configure Git
```bash
cd /Users/g/claude/abetterweather
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Or set globally (for all projects)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 2. Update Files
Replace `yourusername` with your actual GitHub username in:
- `README.md`
- `custom_components/better_mountain_weather/manifest.json`

### 3. Create GitHub Repository
1. Go to https://github.com/new
2. Name: `ha-better-mountain-weather`
3. Public ✓
4. Don't initialize with README
5. Create

### 4. Push Code
```bash
git remote add origin https://github.com/YOUR_USERNAME/ha-better-mountain-weather.git
git push -u origin main
git push origin v0.1.0b1
```

### 5. Create Release
1. Go to your repo → Releases → Draft new release
2. Tag: v0.1.0b1
3. Title: "v0.1.0b1 - Beta 1: AROME Weather Integration"
4. Check "pre-release"
5. Publish

---

**Ready to proceed? Just tell me your GitHub username, name, and email!**
