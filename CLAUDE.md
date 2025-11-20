# PAI Digital Twins Platform - Claude Code Reference

## 🎯 Project Overview

PAI (Personal AI) is a next-generation market research platform that creates queryable digital personas through AI-powered conversational interviews. The platform conducts 15-20 minute natural conversations to extract deep psychological profiles, enabling businesses to query digital twins at scale for market insights with 80%+ accuracy.

## 🎨 UI/UX STANDARDS - MANDATORY REFERENCE

**CRITICAL: Before making ANY UI changes, you MUST read and follow:**
- **`UI_STANDARDS.md`** - Complete UI/UX standard operating procedures

This file contains:
- ✅ Mobile & desktop layout patterns (with NO SCROLL vs SCROLLABLE patterns)
- ✅ Responsive sizing with clamp() - REQUIRED for all dimensions
- ✅ Background system (5 gradient types, full gradient visibility requirement)
- ✅ Typography system (3 font families with complete hierarchy)
- ✅ Reusable components (buttons, headers, cards from globals.css)
- ✅ iOS Safari zoom prevention (16px font-size on inputs)
- ✅ Testing checklists and common mistakes

**When working on UI:**
1. **READ UI_STANDARDS.md first** - Don't guess, follow the documented patterns
2. **Check globals.css** - Button/component you need likely already exists
3. **Use existing patterns** - Don't reinvent layouts, use documented structures
4. **Test on mobile** - All screens must work on iPhone SE (375px)
5. **Verify gradients** - Full gradient must be visible without scrolling

## 🏗️ Architecture

### Frontend: Next.js 15 with App Router
- **Framework**: Next.js 15, TypeScript, Tailwind CSS
- **Voice Integration**: Real-time speech recognition and OpenAI Realtime API
- **Key Components**:
  - `RealtimeVoiceChat.tsx` - Main voice interview component
  - Consumer dashboard and interview flows
  - Multi-twin market research interface
  - Custom questionnaire builder

### Backend: Python Serverless Functions
- **Location**: `/api/` directory (NOT in src/)
- **Architecture**: Vercel serverless functions with Python runtime
- **Main API**: `interview.py` - Handles all interview operations
- **AI Components**:
  - `lib/ai_interviewer.py` - Conversational AI interviewer with self-completion
  - `lib/supabase.py` - Database integration and operations
  - `lib/profile_extractor.py` - Psychological profile builder
  - `lib/response_predictor.py` - Behavioral prediction engine
- **API Actions**: `realtime-token`, `extract_profile`, `save_conversation`, `complete`, `multi-query`

#### Core Backend Components

**1. AI Interviewer (`lib/ai_interviewer.py`)**
- Conducts natural 15-20 minute conversational interviews
- Uses sophisticated prompts to explore attitudes, behaviors, and decision-making
- Claude self-completion system with `[INTERVIEW_COMPLETE]` signal
- Adaptive follow-up questions based on responses
- Real-time transcript and conversation storage

**2. Profile Extractor (`lib/profile_extractor.py`)**
- Converts interview transcripts into structured JSON profiles
- Extracts behavioral patterns, value systems, and prediction weights
- Creates rich digital personas capturing decision-making psychology
- Supports modular questionnaire data combination

**3. Response Predictor (`lib/response_predictor.py`)**
- Takes profiles and predicts behavioral responses with reasoning
- 5-step prediction process with confidence scoring
- Generates detailed explanations for each prediction
- Multi-twin research with privacy-first aggregation

**4. Supabase Integration (`lib/supabase.py`)**
- Direct PostgreSQL database operations
- Profile versioning and session management
- Real-time conversation storage during interviews
- User authentication and data persistence

### Database: Supabase (PostgreSQL)
- **11 implemented tables** supporting comprehensive persona management
- **Key tables**: people, profile_versions, interview_sessions, custom_questionnaires
- **Features**: Profile versioning, modular questionnaires, validation testing

## 🔄 Core Workflow

### Interview Process
1. **Voice Chat Setup**: OpenAI Realtime API with 24kHz audio processing
2. **AI Interview**: Natural conversation following questionnaire structure (29 questions)
3. **Progress Tracking**: Exchange count increments when AI finishes speaking
4. **Conversation Storage**: Real-time saving to Supabase interview_sessions
5. **Completion**: Auto-triggered when AI calls `end_call_tool` function
6. **Profile Extraction**: AI analyzes transcript to create psychological profile

### Questionnaire System
- **Centrepiece**: Core personality (required, ~15 min)
- **Category**: Beauty, fitness, nutrition (~10 min each)
- **Product**: Moisturizer, sunscreen (~5 min each)
- **Modular**: Users select multiple questionnaires in one session

## 🛠️ Technical Specifications

### Development Commands
```bash
npm run dev          # Start development server
npm run build        # Production build
npm run lint         # Code linting
```

### API Endpoints
- `POST /api/interview?action=realtime-token` - Get OpenAI session token
- `POST /api/interview?action=save_conversation` - Store conversation progress
- `POST /api/interview?action=extract_profile` - Complete interview and extract profile
- `POST /api/interview?action=complete` - Handle interview completion

### Environment Variables Required
- `ANTHROPIC_API_KEY` - For AI interviewer and profile extraction
- `OPENAI_API_KEY` - For real-time voice conversations
- `SUPABASE_URL` and `SUPABASE_ANON_KEY` - Database access

## 🗂️ File Structure
```
/Users/rachita/Projects/Pai/
├── src/app/
│   ├── consumer/
│   │   ├── dashboard/page.tsx     # User dashboard
│   │   └── interview/page.tsx     # Interview interface
│   ├── create-profile/page.tsx    # Profile creation wizard
│   ├── multi-query/page.tsx       # Multi-twin research
│   └── globals.css                # Global styles
├── src/components/
│   └── RealtimeVoiceChat.tsx      # Main voice interview component
├── lib/
│   ├── ai_interviewer.py          # AI conversation logic
│   └── supabase.py                # Database operations
├── api/
│   └── interview.py               # Main API handler (Python serverless)
├── project_description.md         # Detailed project overview
├── DATABASE_SCHEMA.md             # Complete database documentation
└── vercel.json                    # Deployment configuration
```

## 🎯 Recent Fixes & Features

### Mobile-First UI Overhaul (September 2024)
1. **Full-Screen Chat Experience**: Mobile devices now display chat in full 100vh height
2. **Hamburger Drawer Navigation**: Clean slide-out drawer with navigation options
3. **Orange Gradient Background**: Consistent brand gradient across entire mobile experience
4. **Profile Cards Carousel**: Touch-swipeable card display optimized for mobile screens
5. **Responsive Design**: Automatic detection and switching between mobile/desktop layouts
6. **Logo Updates**: Integrated `pai_logo_full.png` for complete branding
7. **TypeScript Improvements**: Fixed all type safety issues for production deployment

### Interview Flow Fixes (September 2024)
1. **System Prompt Enhancement**: AI now follows 29 questionnaire questions in order
2. **Progress Counter**: Fixed exchange counting based on audio completion
3. **Auto-completion**: Interview ends when all questions answered
4. **Conversation Storage**: Real-time saving to Supabase during interview
5. **Profile Extraction**: Sends complete conversation transcript for AI analysis

### Voice Chat Implementation
- **OpenAI Realtime API**: WebSocket connection for real-time audio
- **Audio Processing**: 24kHz PCM conversion and playback queue
- **Transcript Collection**: Real-time conversation logging
- **Error Handling**: Comprehensive connection and audio error management

### Mobile UI Components
- **Dashboard Mobile Layout**: Full-screen chat with hamburger navigation
- **Profile Cards Mobile**: Swipeable carousel with touch gesture support
- **Drawer Navigation**: Slide-in menu with orange gradient background
- **Touch Interactions**: Native mobile gestures for card navigation
- **Responsive Breakpoint**: 768px threshold for mobile/desktop switching

### Database Integration
- **Real-time Storage**: Conversation progress saved during interview
- **Message Format**: Structured user/AI message storage in JSONB
- **Session Management**: Complete interview session lifecycle tracking
- **Profile Linking**: Interview sessions linked to generated profiles

## 🚨 Important Notes for Claude Code

### ⚠️ CRITICAL FILES - NEVER DELETE
**These files are ESSENTIAL for deployment and MUST NEVER be deleted:**
- `package.json` - Project dependencies and build scripts
- `package-lock.json` - Dependency lock file for consistent builds
- `tsconfig.json` - TypeScript configuration
- `vercel.json` - Vercel deployment configuration
- `components.json` - Component library configuration
- `next.config.ts` - Next.js configuration
- `tailwind.config.js` - Tailwind CSS configuration

**Deleting any of these files will break deployment and require restoration from git history.**

### File Locations
- **NO API folder in src/**: All API routes are in root `/api/` directory
- **Python Backend**: Designed for Vercel serverless functions
- **Frontend Only in src/**: React components and Next.js app structure

### Development Workflow
- **Local Development**: Python APIs may need manual testing in production
- **Conversation Testing**: Use browser console to debug voice chat flow
- **Database Access**: Direct Supabase queries for data verification

### Architecture Principles
- **NO localStorage**: The entire application is database-driven. Never use localStorage for state persistence, progress tracking, or session management
- **Database-First**: All user progress, session state, and application state should be stored in and retrieved from Supabase
- **Stateless Components**: Components should derive their state from database queries, not client-side storage

### Common Issues
- **404 on API routes**: Python serverless functions only work in production/Vercel
- **Voice Permission**: Browser microphone access required
- **Exchange Count**: Progress tracking depends on audio completion, not text transcripts
- **IMPORTANT**: Do not test VAPI integration in localhost - it will not work. Deploy to Vercel for testing.

## 🔧 Development Guidelines

### When Making Changes
1. **Voice Chat**: Modify `RealtimeVoiceChat.tsx` for frontend interview logic
2. **AI Behavior**: Update `lib/ai_interviewer.py` for conversation flow
3. **API Logic**: Edit `/api/interview.py` for backend operations (NOT in src/)
4. **Database**: Use Supabase dashboard or `lib/supabase.py` methods - NEVER localStorage
5. **State Management**: Always query database for current state - components should be stateless
6. **Progress Tracking**: Use database sessions to determine user progress and screen state
7. **Mobile UI**: Update `/consumer/dashboard/page.tsx` for mobile chat experience
8. **Profile Cards**: Modify `/consumer/profile/page.tsx` for card display and interactions

### Testing Interview Flow
1. Start dev server: `npm run dev`
2. Navigate to `/consumer/interview`
3. Test voice permissions and audio recording
4. Check browser console for debug logs
5. Verify conversation storage in Supabase

## 🎨 Design System

### Typography
The platform uses **Merriweather** as the primary font family and **Instrument Sans** for chat interfaces:

#### Font Families
- **Merriweather** (serif): All text except chat interfaces and display headings
  - Weights: 300 (Light), 400 (Regular)
  - Google Font import: `'Merriweather', Georgia, serif`
- **Instrument Serif** (serif): Display headings only
  - Weight: 400 (Regular)
  - Google Font import: `'Instrument Serif', Georgia, serif`
- **Instrument Sans** (sans-serif): Chat and conversational UI only
  - Weights: 400 (Regular), 500 (Medium), 600 (SemiBold)
  - Google Font import: `'Instrument Sans', sans-serif`

#### Font Hierarchy
- **Display Heading**: Instrument Serif Regular, 64pt, Sentence Case
  - Use ONLY for onboarding headings (Welcome screens, major transitions)
  - Class: `.display-heading`
- **Heading**: Merriweather Regular, 24pt, Sentence Case
  - Section headings, card titles, page titles
  - Class: `.heading`
- **Body**: Merriweather Light, 20pt
  - Main body text, descriptions (default body font)
  - Class: `.body-text`
- **In-Product Chat**: Instrument Sans, 14pt
  - Chat messages, conversational UI
  - Class: `.chat-text`
- **Button**: Merriweather Light, 14pt
  - Button labels, CTAs
  - Class: `.button-text`
- **Text Boxes**: Merriweather Light, 14pt, COLOR 75%
  - Form inputs, text fields
  - Class: `.input-text`

### Background System
The platform uses a split-background design with solid beige top and gradient bottom:

#### Base Structure
- **Top 50%**: Solid #F3EEE8 (beige)
- **Bottom 50%**: Gradient overlay (varies by screen)
- **Border**: 1px solid #000
- **Shadow**: 0 4px 4px 0 rgba(0, 0, 0, 0.25)

#### Background Variants (RESPONSIVE GRADIENTS)

**ALL gradient backgrounds automatically adjust based on viewport height to ensure full gradient visibility on all devices.**

Gradient stops use CSS custom properties that change via media queries:
- **Desktop (> 1024px)**: Original spacing (e.g., 0%, 37.02%, 100%)
- **Large Mobile (850-1024px)**: Slight compression (e.g., 0%, 34%, 100%)
- **Medium Mobile (750-850px)**: Moderate compression (e.g., 0%, 30%, 100%)
- **Small Mobile (< 750px)**: Aggressive compression (e.g., 0%, 25%, 100%)

**1. Default (`.split-background`)**
- Used on: Landing, Intro, Sign In, Sign Up, Welcome Animation, Profile, Dashboard, Brand
- Gradient: `linear-gradient(to top, #EFB79C var(--gradient-stop-1), #CBD4E4 var(--gradient-stop-2), #F3EEE8 var(--gradient-stop-3))`
- Colors: Peachy-orange → Lavender → Beige

**2. Preferences (`.preferences-background`)**
- Used on: Create New Profile page
- Gradient: `linear-gradient(to top, #BECFA4 var(--gradient-stop-1), #CBD4E4 var(--gradient-stop-2), #F3EEE8 var(--gradient-stop-3))`
- Colors: Green → Lavender → Beige

**3. Quick Fire (`.quickfire-background`)**
- Used on: QuickFireScreen (trait builder step 3)
- Gradient: `linear-gradient(to top, #EFB79C var(--gradient-stop-1), #BECFA4 var(--gradient-stop-2), #F3EEE8 var(--gradient-stop-3))`
- Colors: Peachy-orange → Green → Beige

**4. Voice Interview (`.voice-interview-background`)**
- Used on: VoiceInterviewScreen (trait builder step 5)
- Gradient: `linear-gradient(to top, #EBB261 var(--gradient-stop-1), rgba(239, 183, 156, 0.55) var(--gradient-stop-4), #CBD4E4 var(--gradient-stop-5), #F3EEE8 var(--gradient-stop-3))`
- Colors: Gold → Peachy (55% opacity) → Lavender → Beige
- Note: Uses 4-color gradient with stop-4 and stop-5

**5. Completion (`.completion-background`)**
- Used on: CompletionScreen (trait builder step 6)
- Gradient: `linear-gradient(to top, #EBB261 var(--gradient-stop-1), rgba(239, 183, 156, 0.55) var(--gradient-stop-4), #CBD4E4 var(--gradient-stop-5), #F3EEE8 var(--gradient-stop-3))`
- Colors: Gold → Peachy (55% opacity) → Lavender → Beige
- Note: Uses 4-color gradient with stop-4 and stop-5

### Implementation
All backgrounds use CSS pseudo-elements (`::after`) for the gradient overlay positioned at bottom 50%, with content appearing above via z-index layering.

This platform represents the future of market research - moving from static surveys to dynamic, conversational digital twins that provide deeper insights into human behavior while maintaining privacy and performance standards
- never push code.
- please don't commit. i will do it

## 📱 Mobile No-Scroll Pattern (CRITICAL)

**Problem**: Mobile browsers show scrollbars on screens that should be locked to viewport height.

**Solution**: Use the exact pattern from trait-builder for ALL mobile onboarding screens.

### Required Implementation:

```typescript
// 1. Add state and viewport height tracking
const [isMobile, setIsMobile] = useState(false)

useEffect(() => {
  const setViewportHeight = () => {
    const vh = window.innerHeight * 0.01
    document.documentElement.style.setProperty('--vh', `${vh}px`)
  }

  const checkMobile = () => {
    setIsMobile(window.innerWidth <= 768)
  }

  setViewportHeight()
  checkMobile()

  window.addEventListener('resize', setViewportHeight)
  window.addEventListener('orientationchange', setViewportHeight)
  window.addEventListener('resize', checkMobile)

  return () => {
    window.removeEventListener('resize', setViewportHeight)
    window.removeEventListener('orientationchange', setViewportHeight)
    window.removeEventListener('resize', checkMobile)
  }
}, [])

// 2. Container styling
<div
  className="split-background min-h-screen"
  style={{
    ...(isMobile ? {
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      height: 'calc(var(--vh, 1vh) * 100)',
      maxHeight: 'calc(var(--vh, 1vh) * 100)',
      overflow: 'hidden',
      zIndex: 9999,
      display: 'flex',
      flexDirection: 'column'
    } : {})
  }}
>

// 3. Header styling
<header className="header" style={isMobile ? { flexShrink: 0 } : {}}>

// 4. Main content styling (with vertical centering)
<main style={isMobile ? {
  padding: 0,
  margin: 0,
  flex: 1,
  overflow: 'auto',  // allows scrolling within main if content is too tall
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center'  // CRITICAL for vertical centering
} : {}}>

// OR for simple centered content without scrolling:
<div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
  {/* Your centered content */}
</div>
```

### Key Points:
- **ALWAYS** use `position: fixed` for mobile
- **ALWAYS** use `calc(var(--vh, 1vh) * 100)` for height and maxHeight
- **ALWAYS** use `overflow: hidden` on outer container
- **ALWAYS** use `flex: 1` on main content area
- **ALWAYS** use `flexShrink: 0` on header
- **ALWAYS** use `justifyContent: 'center'` on main for vertical centering
- **NEVER** use just `min-h-screen` and `overflow-hidden` without the full pattern
- For content that needs scrolling: use `overflow: 'auto'` on main with `justifyContent: 'center'`
- For simple centered content: use a child div with `flex: 1, display: flex, alignItems: center, justifyContent: center`

### Pages that MUST use this pattern:
- `/consumer/welcome` ✅
- `/consumer/get-paid` ✅
- `/consumer/value-props` ✅
- `/consumer/signin` ✅
- `/consumer/signup` ✅
- Any other onboarding/intro screens

See `/consumer/trait-builder/page.tsx` for the reference implementation.

### Common Mistakes to Avoid:
❌ Using just `min-h-screen` and `overflow-hidden` without `position: fixed`
❌ Using `100vh` instead of `calc(var(--vh, 1vh) * 100)`
❌ Forgetting `maxHeight` in addition to `height`
❌ Not using `flex: 1` on content areas
❌ Missing `justifyContent: 'center'` for vertical centering
❌ Using `overflow: 'hidden'` on main content (prevents scrolling when needed)