# PAI Brand Demo - Quick Start Guide

## What This Demo Does

This is a **standalone brand-side demo** that allows prospective brands to experience PAI's AI digital twin consumer insights platform. Brands can ask up to **10 queries** about consumer preferences for either **Pickles** or **Overnight Oats**.

## Key Features

✅ **Product Selection**: Choose between two product categories
✅ **Real AI Twins**: Queries actual digital twin profiles from your Supabase database
✅ **AI-Powered Insights**: Uses Claude Sonnet 4.5 to analyze and aggregate responses
✅ **Chat Interface**: Natural conversation-style with suggested questions
✅ **Mobile-First Design**: Follows PAI design system with responsive gradients
✅ **Query Limiting**: Restricts to 10 queries per demo session

## Quick Setup

### 1. Environment Variables Needed

Create `.env.local` with:

```env
NEXT_PUBLIC_SUPABASE_URL=<from main Pai project>
NEXT_PUBLIC_SUPABASE_ANON_KEY=<from main Pai project>
SUPABASE_SERVICE_ROLE_KEY=<from main Pai project>
ANTHROPIC_API_KEY=<your anthropic key>
```

### 2. Run Locally

```bash
npm run dev
```

Open http://localhost:3000

**Note**: The Python API endpoints (`/api/query`) will **NOT work in localhost**. They only work when deployed to Vercel (serverless functions limitation).

### 3. Deploy to Vercel

```bash
vercel deploy
```

Add the environment variables in Vercel dashboard → Settings → Environment Variables.

## User Flow

1. **Landing Page** (`/`)
   - User sees two product cards: Pickles 🥒 and Overnight Oats 🥣
   - Clicks to select a product
   - Clicks "Continue to Demo"

2. **Chat Demo** (`/demo?product=pickles`)
   - Welcome message explains the demo
   - Shows 4 suggested consumer insights questions
   - User can click suggestions or type custom questions
   - Query counter shows remaining queries (e.g., "3/10 queries")

3. **Query Processing**
   - Question sent to `/api/query`
   - API fetches 5 active AI twin profiles from Supabase
   - Claude Sonnet 4.5 analyzes profiles and generates insights
   - Response appears in chat (150-250 words)

4. **Query Limit**
   - After 10 queries, input is disabled
   - Shows "Start New Demo" button to reset

## Technical Architecture

```
┌─────────────────────────────────────────────────────────┐
│  User Clicks Product (Pickles/Oats)                    │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  Chat Interface (/demo)                                 │
│  - Shows suggested questions                            │
│  - Tracks query count                                   │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  POST /api/query (Python Serverless)                    │
│  - Receives: { product, question }                      │
│  - Returns: { response, profiles_analyzed, product }    │
└────────────────────┬────────────────────────────────────┘
                     ↓
        ┌────────────┴────────────┐
        ↓                         ↓
┌──────────────────┐    ┌──────────────────────┐
│  Supabase        │    │  Claude Sonnet 4.5   │
│  (Get 5 active   │    │  (Analyze profiles   │
│   AI twin        │───→│   Generate insights) │
│   profiles)      │    │                      │
└──────────────────┘    └──────────────────────┘
```

## Suggested Questions by Product

### Pickles 🥒
- "What flavor profiles do consumers prefer in pickles?"
- "How important is organic certification for pickle buyers?"
- "What packaging formats are most appealing?"
- "How often do consumers buy pickles?"
- "What price points are considered reasonable?"
- "Do consumers prefer traditional or innovative flavors?"
- "What health benefits do consumers associate with pickles?"
- "How do consumers typically consume pickles?"

### Overnight Oats 🥣
- "What flavors are most popular for overnight oats?"
- "How important is convenience in breakfast choices?"
- "What nutritional attributes matter most?"
- "How much are consumers willing to pay?"
- "Do consumers prefer ready-made or DIY overnight oats?"
- "What time-saving benefits resonate most?"
- "How important is sustainability in packaging?"
- "What add-ins do consumers prefer?"

## Design System

### Fonts (Loaded via Google Fonts)
- **Merriweather**: Primary body font (300, 400)
- **Instrument Serif**: Display headings (400)
- **Instrument Sans**: Chat interface (400, 500, 600)

### Colors
- Background: Beige (#F3EEE8) top, gradient bottom (peachy to lavender)
- Primary Button: Black background, white text
- User Messages: Black bubble, white text
- AI Messages: White bubble, black text

### Responsive Design
- All dimensions use `clamp()` for fluid scaling
- Mobile breakpoint: 768px
- iOS Safari zoom prevention: 16px input font-size
- Full gradient visibility on all screen heights

## API Endpoint Details

### POST `/api/query`

**Request:**
```json
{
  "product": "pickles",
  "question": "What flavor profiles do consumers prefer?"
}
```

**Response:**
```json
{
  "response": "Based on analysis of 5 digital twins...",
  "profiles_analyzed": 5,
  "product": "pickles"
}
```

**Process:**
1. Validates product and question
2. Queries `profile_versions` table for active profiles
3. Filters for profiles with food/lifestyle data
4. Takes up to 5 profiles
5. Formats profiles for Claude
6. Generates insights using Claude Sonnet 4.5
7. Returns aggregated insights (150-250 words)

## Database Requirements

The demo expects these tables in Supabase:

- **profile_versions**: Contains AI twin profile data
  - `profile_id`: Unique identifier
  - `is_active`: Boolean (must be true)
  - `profile_data`: JSONB with twin data
    - Can include: `demographics`, `eating_habits`, `purchase_behavior`, `health_wellness`, etc.

## Costs Estimation

Per query:
- 1 Claude Sonnet 4.5 API call (~$0.015)
- 1 Supabase read (negligible)

For 10 queries: ~$0.15 per demo session

## Limitations & Notes

⚠️ **API endpoints don't work in localhost** - deploy to Vercel to test
⚠️ **No session persistence** - refresh resets query count
⚠️ **No rate limiting** - add if needed for production
⚠️ **Fixed to 2 products** - easy to expand in `SUGGESTED_QUESTIONS` object

## Files Structure

```
/brand
├── app/
│   ├── page.tsx              # Product selection
│   ├── demo/page.tsx         # Chat interface
│   ├── layout.tsx            # Fonts + metadata
│   └── globals.css           # Design system
├── api/
│   └── query.py              # Insights API
├── lib/
│   ├── supabase.py           # DB client
│   └── insights_generator.py # Claude integration
├── vercel.json               # Serverless config
├── requirements.txt          # Python deps
└── README.md                 # Full documentation
```

## Deployment Checklist

- [ ] Copy environment variables to Vercel
- [ ] Verify Supabase has active AI twin profiles
- [ ] Test API endpoint by asking a question
- [ ] Verify query limit works (stops at 10)
- [ ] Test on mobile device (responsive design)
- [ ] Share demo link with prospective brands!

## Troubleshooting

**Q: "I get 'No profiles available'"**
A: Check that your Supabase `profile_versions` table has profiles with `is_active=true`

**Q: "API endpoint returns 500 error"**
A: Check Vercel logs for Python errors. Verify `ANTHROPIC_API_KEY` is set.

**Q: "Chat looks broken on mobile"**
A: Make sure viewport height CSS variables are working. Check browser console.

**Q: "Insights seem generic"**
A: Profiles might lack detailed data. Add more fields to `profile_data` JSONB.

## Next Steps for Production

1. Add session persistence (store in database or localStorage)
2. Implement rate limiting per IP/email
3. Add more product categories
4. Create admin dashboard to manage demos
5. Add analytics tracking
6. Export insights as PDF
7. Custom branding per demo link
8. Email capture before demo access
