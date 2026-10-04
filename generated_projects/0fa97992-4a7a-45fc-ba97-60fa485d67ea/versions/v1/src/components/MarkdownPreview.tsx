import React from 'react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

interface MarkdownPreviewProps {
  content: string;
}

// Configure marked options for safe rendering and GFM support
marked.setOptions({
  gfm: true,
  breaks: true,
});

export const MarkdownPreview: React.FC<MarkdownPreviewProps> = ({ content }) => {
  // Parse markdown string into HTML safely and sanitize with DOMPurify to prevent XSS
  const getSanitizedHtml = (markdownText: string) => {
    try {
      const rawHtml = marked.parse(markdownText || '') as string;
      return DOMPurify.sanitize(rawHtml);
    } catch (error) {
      console.error('Error parsing markdown:', error);
      return '<p class="text-red-500">Error rendering preview</p>';
    }
  };

  return (
    <div className="h-full overflow-y-auto px-6 py-4 bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200">
      <div
        className="prose dark:prose-invert max-w-none prose-headings:font-bold prose-a:text-blue-600 hover:prose-a:underline"
        dangerouslySetInnerHTML={{ __html: getSanitizedHtml(content) }}
      />
    </div>
  );
};
