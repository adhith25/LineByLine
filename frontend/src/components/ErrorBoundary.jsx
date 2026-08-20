import React from 'react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({ errorInfo });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div
          className="card-box"
          style={{
            margin: 20,
            border: '1px solid var(--danger)',
            background: 'rgba(239, 68, 68, 0.06)',
            maxWidth: 560,
          }}
        >
          <div className="card-title" style={{ color: '#fca5a5' }}>
            <span>🚨</span>
            <span>Something went wrong</span>
          </div>
          <div style={{ fontSize: 13, color: '#fecaca', lineHeight: 1.6, marginBottom: 14 }}>
            The UI hit an unexpected error while rendering this section.
            {this.state.error && (
              <div
                style={{
                  marginTop: 10,
                  padding: '10px 12px',
                  background: 'rgba(0,0,0,0.25)',
                  borderRadius: 8,
                  fontFamily: 'var(--font-mono)',
                  fontSize: 11.5,
                  color: '#fca5a5',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}
              >
                {this.state.error.message || String(this.state.error)}
              </div>
            )}
          </div>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            <button className="btn-primary" style={{ width: 'auto', fontSize: 13, padding: '8px 16px' }} onClick={this.handleReset}>
              ↺ Retry Render
            </button>
            <button
              className="btn-secondary"
              onClick={() => window.location.reload()}
            >
              🔄 Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
