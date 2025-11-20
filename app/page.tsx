'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();
  const [selectedProduct, setSelectedProduct] = useState<string | null>(null);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const setViewportHeight = () => {
      const vh = window.innerHeight * 0.01;
      document.documentElement.style.setProperty('--vh', `${vh}px`);
    };

    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    setViewportHeight();
    checkMobile();

    window.addEventListener('resize', setViewportHeight);
    window.addEventListener('orientationchange', setViewportHeight);
    window.addEventListener('resize', checkMobile);

    return () => {
      window.removeEventListener('resize', setViewportHeight);
      window.removeEventListener('orientationchange', setViewportHeight);
      window.removeEventListener('resize', checkMobile);
    };
  }, []);

  const handleProductSelect = (product: string) => {
    setSelectedProduct(product);
  };

  const handleContinue = () => {
    if (selectedProduct) {
      router.push(`/demo?product=${selectedProduct}`);
    }
  };

  return (
    <div
      className="split-background min-h-screen"
      style={{
        ...(isMobile
          ? {
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
              flexDirection: 'column',
            }
          : {}),
      }}
    >
      {/* Header */}
      <header className="header" style={isMobile ? { flexShrink: 0 } : {}}>
        <div
          style={{
            maxWidth: '1200px',
            margin: '0 auto',
            padding: '0 24px',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <img
                src="/pai_logo_full_black.png"
                alt="PAI"
                className="logo-image"
                style={{ height: 'clamp(32px, 6vw, 48px)' }}
              />
            </div>
            <div
              style={{
                backgroundColor: 'rgba(17, 24, 39, 0.1)',
                border: '1px solid rgba(17, 24, 39, 0.2)',
                borderRadius: '20px',
                padding: '6px 16px',
                fontSize: '12px',
                fontWeight: 500,
                color: '#374151',
              }}
            >
              Brand Demo
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main
        style={
          isMobile
            ? {
                padding: 0,
                margin: 0,
                flex: 1,
                overflow: 'auto',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
              }
            : {
                padding: '64px 0',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                minHeight: 'calc(100vh - 120px)',
              }
        }
      >
        <div
          style={{
            maxWidth: '1000px',
            margin: '0 auto',
            padding: '0 24px',
            width: '100%',
          }}
        >
          {/* Hero Text */}
          <div style={{ textAlign: 'center', marginBottom: 'clamp(32px, 6vh, 48px)' }}>
            <h1 className="display-heading" style={{ marginBottom: 'clamp(12px, 2vh, 16px)' }}>
              Query AI Twins
            </h1>
            <p className="body-text" style={{ maxWidth: '600px', margin: '0 auto', opacity: 0.8 }}>
              Get instant consumer insights by asking questions to our AI-powered digital personas.
              Select a product to begin.
            </p>
          </div>

          {/* Product Selection Cards */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: isMobile ? '1fr' : 'repeat(2, 1fr)',
              gap: 'clamp(16px, 3vw, 24px)',
              marginBottom: 'clamp(24px, 4vh, 32px)',
            }}
          >
            {/* Pickles Card */}
            <div
              className={`product-card ${selectedProduct === 'pickles' ? 'selected' : ''}`}
              onClick={() => handleProductSelect('pickles')}
            >
              <div style={{ fontSize: 'clamp(36px, 8vw, 48px)', marginBottom: '12px', textAlign: 'center' }}>
                🥒
              </div>
              <h3 className="heading" style={{ textAlign: 'center', marginBottom: '8px' }}>
                Pickles
              </h3>
              <p className="body-text" style={{ textAlign: 'center', fontSize: 'clamp(12px, 2vw, 14px)', opacity: 0.7 }}>
                Understand consumer preferences for artisanal pickles and fermented foods
              </p>
            </div>

            {/* Overnight Oats Card */}
            <div
              className={`product-card ${selectedProduct === 'oats' ? 'selected' : ''}`}
              onClick={() => handleProductSelect('oats')}
            >
              <div style={{ fontSize: 'clamp(36px, 8vw, 48px)', marginBottom: '12px', textAlign: 'center' }}>
                🥣
              </div>
              <h3 className="heading" style={{ textAlign: 'center', marginBottom: '8px' }}>
                Overnight Oats
              </h3>
              <p className="body-text" style={{ textAlign: 'center', fontSize: 'clamp(12px, 2vw, 14px)', opacity: 0.7 }}>
                Discover insights about healthy breakfast habits and convenience foods
              </p>
            </div>
          </div>

          {/* Continue Button */}
          <div style={{ textAlign: 'center' }}>
            <button
              className="btn-primary"
              onClick={handleContinue}
              disabled={!selectedProduct}
              style={{
                opacity: selectedProduct ? 1 : 0.5,
                cursor: selectedProduct ? 'pointer' : 'not-allowed',
                minWidth: 'clamp(160px, 30vw, 200px)',
              }}
            >
              Continue to Demo
            </button>
          </div>

          {/* Demo Info */}
          <div style={{ textAlign: 'center', marginTop: 'clamp(24px, 4vh, 32px)' }}>
            <p className="body-text" style={{ fontSize: 'clamp(11px, 1.8vw, 13px)', opacity: 0.6 }}>
              You'll have <strong>10 queries</strong> to ask our AI digital twins
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
