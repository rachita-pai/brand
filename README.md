# PAI Brand Demo

A standalone demo experience for prospective brands to explore PAI's AI digital twin consumer insights platform.

## Overview

This demo allows brands to:
- Select a product category (Pickles or Overnight Oats)
- Ask up to 10 consumer insights questions
- Receive aggregated insights from real AI digital twin profiles
- Experience the power of conversational AI-driven market research

## Features

- **Product Selection**: Choose between pickles and overnight oats
- **Chat Interface**: Natural conversation-style query interface
- **Suggested Questions**: Pre-started consumer insights questions to get started
- **Real AI Twins**: Queries actual digital twin profiles from Supabase
- **AI-Powered Insights**: Uses Claude Sonnet 4.5 to generate aggregated insights
- **Query Limit**: 10 queries per demo session to manage API costs
- **Mobile-First**: Fully responsive design following PAI design system

## Tech Stack

- **Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS
- **Backend**: Python serverless functions (Vercel)
- **Database**: Supabase (PostgreSQL)
- **AI**: Claude Sonnet 4.5 (Anthropic)
- **Design**: PAI design system (Merriweather, Instrument Serif, Instrument Sans)

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Environment Variables

Copy `.env.example` to `.env.local`:

```bash
cp .env.example .env.local
```

Fill in your environment variables:

```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the demo.

## Project Structure

```
/brand
├── app/
│   ├── page.tsx              # Product selection landing page
│   ├── demo/
│   │   └── page.tsx          # Chat interface for queries
│   ├── layout.tsx            # Root layout with fonts
│   └── globals.css           # PAI design system styles
├── api/
│   └── query.py              # Python serverless API for insights
├── lib/
│   ├── supabase.py           # Supabase client
│   └── insights_generator.py # Claude-powered insights generator
├── CLAUDE.md                 # PAI project reference documentation
└── README.md                 # This file
```

## How It Works

### 1. Product Selection (`/`)
- User selects either Pickles or Overnight Oats
- Responsive cards with hover effects
- Continues to demo with selected product

### 2. Chat Demo (`/demo?product={product}`)
- Displays suggested consumer insights questions
- User can ask custom questions or click suggestions
- Each query is sent to `/api/query`

### 3. API Processing (`/api/query.py`)
- Receives product category and question
- Queries Supabase for active AI digital twin profiles
- Filters for profiles with relevant food/lifestyle data
- Passes profiles and question to Claude Sonnet 4.5
- Returns aggregated consumer insights

### 4. Insights Generation
- Claude analyzes multiple twin profiles
- Provides percentage breakdowns and patterns
- Cites specific behaviors and preferences
- Returns actionable insights for brands

## Design System

### Typography
- **Display Heading**: Instrument Serif, 64px (fluid responsive)
- **Heading**: Merriweather Regular, 24px (fluid responsive)
- **Body**: Merriweather Light, 16px (fluid responsive)
- **Chat**: Instrument Sans, 14px

### Colors
- **Background**: Split gradient (beige top, peachy-lavender bottom)
- **Primary Button**: Black with white text
- **Chat Bubbles**: User (black), Assistant (white)

### Mobile-First
- Fully responsive with clamp() for all dimensions
- iOS Safari zoom prevention (16px input font-size)
- Touch-friendly hit areas
- Smooth animations and transitions

## Deployment

This project is designed to deploy on Vercel:

```bash
vercel deploy
```

Make sure to add environment variables in Vercel dashboard.

## Limitations

- **Demo Mode**: Limited to 10 queries per session
- **Product Categories**: Only pickles and overnight oats for demo
- **Profile Availability**: Requires active AI twin profiles in database
- **Rate Limiting**: No rate limiting implemented (should add for production)

## Future Enhancements

- [ ] Session persistence (save query history)
- [ ] Export insights as PDF
- [ ] More product categories
- [ ] Admin dashboard to manage demo settings
- [ ] Analytics tracking for demo usage
- [ ] Custom branding per demo link
- [ ] Rate limiting and abuse prevention

## License

Proprietary - PAI Platform
