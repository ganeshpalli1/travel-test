# 🚀 Deploy to Vercel - Step by Step Guide

## Prerequisites
1. **Vercel Account** - Sign up at [vercel.com](https://vercel.com)
2. **GitHub Account** - For code repository
3. **Perplexity API Key** - Get from [perplexity.ai](https://perplexity.ai)

## 📋 Step 1: Prepare Your Repository

### Upload to GitHub:
1. Create a new repository on GitHub
2. Upload all your project files:
   ```
   ishan-backend/
   ├── app.py
   ├── travel_assistant.py
   ├── vercel.json
   ├── requirements.txt
   ├── .vercelignore
   ├── api/
   │   └── index.py
   └── static/
       ├── index.html
       ├── style.css
       └── script.js
   ```

## 🌐 Step 2: Deploy to Vercel

### Option A: Deploy via Vercel Dashboard
1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click **"New Project"**
3. **Import** your GitHub repository
4. **Framework Preset**: Select "Other"
5. **Root Directory**: Leave as "." (root)
6. Click **"Deploy"**

### Option B: Deploy via Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Follow the prompts:
# ? Set up and deploy "ishan-backend"? [Y/n] y
# ? Which scope? [Your username]
# ? Link to existing project? [y/N] n
# ? What's your project's name? travel-assistant
# ? In which directory is your code located? ./
```

## 🔑 Step 3: Set Environment Variables

### In Vercel Dashboard:
1. Go to your project dashboard
2. Click **"Settings"** tab
3. Click **"Environment Variables"**
4. Add:
   - **Name**: `PERPLEXITY_API_KEY`
   - **Value**: Your actual Perplexity API key
   - **Environment**: All (Production, Preview, Development)
5. Click **"Save"**

### Via CLI:
```bash
vercel env add PERPLEXITY_API_KEY
# Enter your API key when prompted
```

## ✅ Step 4: Verify Deployment

1. **Visit Your Site**: Check the URL Vercel provides
2. **Test API Health**: Visit `https://your-app.vercel.app/api/health`
3. **Test Chat**: Try asking a travel question

## 🔧 Step 5: Custom Domain (Optional)

1. In Vercel dashboard, go to **"Domains"**
2. Add your custom domain
3. Configure DNS records as instructed

## 🚨 Troubleshooting

### Common Issues:

1. **"PERPLEXITY_API_KEY not found"**
   - Add the environment variable in Vercel dashboard
   - Redeploy after adding

2. **"Static files not found"**
   - Ensure `static/` folder is in your repository
   - Check `.vercelignore` doesn't exclude static files

3. **"Function timeout"**
   - Vercel has a 10-second timeout for Hobby plans
   - Consider upgrading for longer requests

4. **"Import errors"**
   - Check all dependencies are in `requirements.txt`
   - Ensure Python version compatibility

### Debug Steps:
1. Check **Vercel Function Logs** in dashboard
2. Test **API endpoints** individually
3. Verify **environment variables** are set
4. Check **build logs** for errors

## 🎉 Success!

Your travel chatbot should now be live at:
- **Main App**: `https://your-project.vercel.app`
- **API Health**: `https://your-project.vercel.app/api/health`
- **Chat API**: `https://your-project.vercel.app/api/chat`

## 📝 Pro Tips:

1. **Custom Domain**: Add a custom domain for professional look
2. **Analytics**: Enable Vercel Analytics in dashboard
3. **Monitoring**: Set up uptime monitoring
4. **Caching**: Leverage Vercel's edge caching
5. **Git Integration**: Auto-deploy on commits to main branch

Happy deploying! 🌍✈️ 