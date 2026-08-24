import React, { useEffect } from 'react';

// Component to load the chat widget script
const ChatScriptLoader = () => {
  useEffect(() => {
    if (!document.querySelector('script[src*="flowos-embedded-chat"]')) {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/gh/flowos-ai/flowos-embedded-chat@main/dist/build/static/js/bundle.min.js';
      script.async = true;
      document.body.appendChild(script);
    }
  }, []);

  return null;
};

declare global {
    namespace JSX {
      interface IntrinsicElements {
        "flowos-chat": any;
      }
    }
  }

  export default function ChatWidget({ className }) {
    return (
      <div className={className}>
        <ChatScriptLoader />
        <flowos-chat
          host_url="http://localhost:7860"
          flow_id="YOUR_FLOW_ID"
        ></flowos-chat>
      </div>
    );
  }