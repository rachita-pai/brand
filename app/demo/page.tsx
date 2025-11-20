'use client';

import { useState, useEffect, useRef, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';

// Suggested questions for each product
const SUGGESTED_QUESTIONS = {
  pickles: [
    "What flavor profiles do consumers prefer in pickles?",
    "How important is organic certification for pickle buyers?",
    "What packaging formats are most appealing?",
    "How often do consumers buy pickles?",
    "What price points are considered reasonable?",
    "Do consumers prefer traditional or innovative flavors?",
    "What health benefits do consumers associate with pickles?",
    "How do consumers typically consume pickles?",
  ],
  oats: [
    "What flavors are most popular for overnight oats?",
    "How important is convenience in breakfast choices?",
    "What nutritional attributes matter most?",
    "How much are consumers willing to pay?",
    "Do consumers prefer ready-made or DIY overnight oats?",
    "What time-saving benefits resonate most?",
    "How important is sustainability in packaging?",
    "What add-ins do consumers prefer?",
  ],
};

interface SurveyData {
  total_twins_queried: number;
  confidence: number;
  key_insights: string[];
  survey_results: Array<{
    question: string;
    top_insight: string;
    data_points: Array<{
      category: string;
      percentage: number;
      description?: string;
    }>;
    confidence: number;
  }>;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  surveyData?: SurveyData;
}

// Survey Results Display Component with Charts
const SurveyResultsDisplay = ({ data }: { data: SurveyData }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);

  if (!data || !data.survey_results) return null;

  const colors = ['#93C5FD', '#86EFAC', '#FDE68A', '#DDD6FE'];

  return (
    <div style={{ width: '100%', maxWidth: '100%' }}>
      {/* Summary Card */}
      <div style={{ marginBottom: '16px', padding: 'clamp(12px, 3vw, 16px)', backgroundColor: 'white', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
        <div style={{ fontSize: 'clamp(13px, 2.5vw, 15px)', fontWeight: '600', marginBottom: '12px' }}>
          Survey Results from AI Twins:
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'clamp(8px, 2vw, 12px)', marginBottom: '16px' }}>
          <div style={{ padding: 'clamp(10px, 2.5vw, 14px)', backgroundColor: '#f9fafb', borderRadius: '8px' }}>
            <div style={{ fontSize: 'clamp(18px, 4vw, 22px)', fontWeight: '700' }}>{data.total_twins_queried?.toLocaleString()}</div>
            <div style={{ fontSize: 'clamp(11px, 2vw, 13px)', color: '#6b7280' }}>Twins Surveyed</div>
          </div>
          <div style={{ padding: 'clamp(10px, 2.5vw, 14px)', backgroundColor: '#f9fafb', borderRadius: '8px' }}>
            <div style={{ fontSize: 'clamp(18px, 4vw, 22px)', fontWeight: '700' }}>{data.confidence}%</div>
            <div style={{ fontSize: 'clamp(11px, 2vw, 13px)', color: '#6b7280' }}>Confidence</div>
          </div>
        </div>

        <div style={{ fontSize: 'clamp(13px, 2.5vw, 15px)', fontWeight: '600', marginBottom: '8px' }}>💡 Key Insights</div>
        {data.key_insights?.map((insight: string, i: number) => (
          <div key={i} style={{ marginBottom: '6px', fontSize: 'clamp(12px, 2.2vw, 13px)' }}>
            <strong>{i + 1}.</strong> {insight}
          </div>
        ))}
      </div>

      {/* Survey Data Cards */}
      <div style={{ padding: 'clamp(12px, 3vw, 16px)', backgroundColor: 'white', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div style={{ fontSize: 'clamp(13px, 2.5vw, 15px)', fontWeight: '600' }}>📋 Detailed Analysis</div>
          <div style={{ fontSize: 'clamp(11px, 2vw, 13px)', color: '#6b7280' }}>{data.survey_results.length} questions</div>
        </div>

        {/* Current Question Card */}
        {data.survey_results[currentQuestion] && (
          <div>
            <div style={{ padding: 'clamp(12px, 3vw, 14px)', backgroundColor: '#f9fafb', borderRadius: '8px', marginBottom: '12px', borderLeft: '4px solid #000' }}>
              <div style={{ fontSize: 'clamp(13px, 2.5vw, 15px)', fontWeight: '600', marginBottom: '6px' }}>
                {data.survey_results[currentQuestion].question}
              </div>
              <div style={{ fontSize: 'clamp(12px, 2.2vw, 13px)', color: '#6b7280', fontStyle: 'italic' }}>
                💡 {data.survey_results[currentQuestion].top_insight}
              </div>
            </div>

            {/* Bar Chart */}
            <div style={{ marginBottom: '16px' }}>
              {data.survey_results[currentQuestion].data_points?.map((dp, i: number) => (
                <div key={i} style={{ marginBottom: '10px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span style={{ fontSize: 'clamp(12px, 2.2vw, 13px)', fontWeight: '500' }}>{dp.category}</span>
                    <span style={{ fontSize: 'clamp(12px, 2.2vw, 13px)', fontWeight: '700' }}>{dp.percentage}%</span>
                  </div>
                  <div style={{ width: '100%', height: 'clamp(20px, 4vw, 24px)', backgroundColor: '#e5e7eb', borderRadius: '4px', overflow: 'hidden' }}>
                    <div
                      style={{
                        width: `${dp.percentage}%`,
                        height: '100%',
                        backgroundColor: colors[i % colors.length],
                        transition: 'width 0.5s ease'
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* Navigation Dots */}
            <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', alignItems: 'center' }}>
              <button
                onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
                disabled={currentQuestion === 0}
                style={{
                  padding: 'clamp(6px, 1.5vw, 8px) clamp(10px, 2.5vw, 12px)',
                  border: 'none',
                  borderRadius: '50%',
                  backgroundColor: currentQuestion === 0 ? '#e5e7eb' : '#f3f4f6',
                  cursor: currentQuestion === 0 ? 'not-allowed' : 'pointer',
                  fontSize: 'clamp(14px, 3vw, 16px)'
                }}
              >
                ←
              </button>

              {data.survey_results.map((_survey, i: number) => (
                <div
                  key={i}
                  onClick={() => setCurrentQuestion(i)}
                  style={{
                    width: 'clamp(8px, 2vw, 10px)',
                    height: 'clamp(8px, 2vw, 10px)',
                    borderRadius: '50%',
                    backgroundColor: i === currentQuestion ? '#000' : '#d1d5db',
                    cursor: 'pointer',
                    transition: 'background-color 0.3s'
                  }}
                />
              ))}

              <button
                onClick={() => setCurrentQuestion(Math.min(data.survey_results.length - 1, currentQuestion + 1))}
                disabled={currentQuestion === data.survey_results.length - 1}
                style={{
                  padding: 'clamp(6px, 1.5vw, 8px) clamp(10px, 2.5vw, 12px)',
                  border: 'none',
                  borderRadius: '50%',
                  backgroundColor: currentQuestion === data.survey_results.length - 1 ? '#e5e7eb' : '#f3f4f6',
                  cursor: currentQuestion === data.survey_results.length - 1 ? 'not-allowed' : 'pointer',
                  fontSize: 'clamp(14px, 3vw, 16px)'
                }}
              >
                →
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

function DemoContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const product = searchParams.get('product') as 'pickles' | 'oats';

  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [queriesUsed, setQueriesUsed] = useState(0);
  const [isMobile, setIsMobile] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const MAX_QUERIES = 10;

  useEffect(() => {
    if (!product || (product !== 'pickles' && product !== 'oats')) {
      router.push('/');
      return;
    }

    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);

    // Welcome message
    setMessages([
      {
        id: '1',
        role: 'assistant',
        content: `Welcome to the PAI Demo! I'm analyzing responses from our AI twins of real people regarding ${
          product === 'pickles' ? 'pickles' : 'overnight oats'
        }. You have ${MAX_QUERIES} queries available. Ask me anything about consumer preferences, behaviors, or opinions!`,
        timestamp: new Date(),
      },
    ]);

    return () => {
      window.removeEventListener('resize', checkMobile);
    };
  }, [product, router]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (messageText?: string) => {
    const textToSend = messageText || inputValue.trim();

    if (!textToSend || queriesUsed >= MAX_QUERIES || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: textToSend,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setQueriesUsed((prev) => prev + 1);

    try {
      // Call API to get AI twin responses
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product,
          question: textToSend,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();

      // Check if we have structured survey data or fallback text
      const hasSurveyData = data.survey_results && data.key_insights;

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: hasSurveyData
          ? `Analyzed ${data.total_twins_queried} AI twins with ${data.confidence}% confidence`
          : data.response,
        timestamp: new Date(),
        surveyData: hasSurveyData ? data : undefined,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your question. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
      setQueriesUsed((prev) => prev - 1); // Refund the query
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    if (queriesUsed >= MAX_QUERIES) return;
    handleSendMessage(suggestion);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!product) return null;

  const productEmoji = product === 'pickles' ? '🥒' : '🥣';
  const productName = product === 'pickles' ? 'Pickles' : 'Overnight Oats';
  const suggestions = SUGGESTED_QUESTIONS[product];

  return (
    <div
      className="split-background"
      style={{
        height: '100vh',
        maxHeight: '100vh',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Header */}
      <header className="header" style={{ flexShrink: 0, borderBottom: '1px solid rgba(0, 0, 0, 0.1)' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 24px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', alignItems: 'center', gap: '12px' }}>
            {/* Left: Logo */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-start' }}>
              <img
                src="/pai_logo_full_black.png"
                alt="PAI"
                className="logo-image"
                style={{ height: 'clamp(20px, 3.5vw, 28px)' }}
              />
            </div>

            {/* Center: Product */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', justifyContent: 'center' }}>
              <span style={{ fontSize: 'clamp(20px, 4vw, 28px)' }}>{productEmoji}</span>
              <span className="heading" style={{ margin: 0, fontSize: 'clamp(16px, 3vw, 20px)' }}>
                {productName}
              </span>
            </div>

            {/* Right: Query counter and Back button */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', justifyContent: 'flex-end' }}>
              <div
                style={{
                  backgroundColor: queriesUsed >= MAX_QUERIES ? 'rgba(239, 68, 68, 0.1)' : 'rgba(34, 197, 94, 0.1)',
                  border: `1px solid ${queriesUsed >= MAX_QUERIES ? 'rgba(239, 68, 68, 0.3)' : 'rgba(34, 197, 94, 0.3)'}`,
                  borderRadius: '20px',
                  padding: '6px 16px',
                  fontSize: '12px',
                  fontWeight: 500,
                  color: queriesUsed >= MAX_QUERIES ? '#DC2626' : '#059669',
                }}
              >
                {queriesUsed}/{MAX_QUERIES} queries
              </div>
              <button
                onClick={() => router.push('/')}
                className="btn-secondary"
                style={{ padding: '8px 16px', fontSize: '13px' }}
              >
                ← Back
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Chat Container */}
      <div className="chat-container" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Messages */}
        <div className="chat-messages">
          {messages.map((message) => (
            <div key={message.id} className={`chat-message ${message.role}`}>
              <div className={`message-bubble ${message.role}`}>
                {message.surveyData ? (
                  <SurveyResultsDisplay data={message.surveyData} />
                ) : (
                  message.content
                )}
              </div>
              <span className="message-time">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          ))}
          {isLoading && (
            <div className="chat-message assistant">
              <div className="message-bubble assistant" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div className="loading-spinner"></div>
                <span>Analyzing AI twin responses...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Questions */}
        {messages.length === 1 && queriesUsed === 0 && (
          <div className="suggested-questions" style={{ flexShrink: 0 }}>
            <div style={{ width: '100%', marginBottom: '8px' }}>
              <p className="body-text" style={{ fontSize: '12px', opacity: 0.6, margin: 0 }}>
                Suggested questions:
              </p>
            </div>
            {suggestions.slice(0, 4).map((suggestion, index) => (
              <div
                key={index}
                className="suggestion-chip"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                {suggestion}
              </div>
            ))}
          </div>
        )}

        {/* Input Area */}
        <div className="chat-input-container" style={{ flexShrink: 0 }}>
          {queriesUsed >= MAX_QUERIES ? (
            <div style={{ textAlign: 'center', padding: '16px' }}>
              <p className="body-text" style={{ marginBottom: '12px', color: '#DC2626' }}>
                You've used all {MAX_QUERIES} queries for this demo.
              </p>
              <button onClick={() => router.push('/')} className="btn-primary">
                Start New Demo
              </button>
            </div>
          ) : (
            <div className="chat-input-wrapper">
              <input
                type="text"
                className="chat-input"
                placeholder="Ask a question about consumer insights..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={isLoading}
              />
              <button
                className="send-button"
                onClick={() => handleSendMessage()}
                disabled={!inputValue.trim() || isLoading}
              >
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 20 20"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M18 2L9 11M18 2L12 18L9 11M18 2L2 8L9 11"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function DemoPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <DemoContent />
    </Suspense>
  );
}
