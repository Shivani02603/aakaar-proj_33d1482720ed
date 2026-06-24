import React from 'react';

const TypingIndicator: React.FC = () => {
  return (
    <div className="flex items-center space-x-1">
      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce-dot"></div>
      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce-dot animation-delay-200"></div>
      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce-dot animation-delay-400"></div>
    </div>
  );
};

export default TypingIndicator;

// Tailwind CSS keyframes and animation classes
// Add the following to your Tailwind CSS configuration file under `extend`:

// module.exports = {
//   theme: {
//     extend: {
//       keyframes: {
//         bounceDot: {
//           '0%, 100%': { transform: 'translateY(0)' },
//           '50%': { transform: 'translateY(-0.5rem)' },
//         },
//       },
//       animation: {
//         'bounce-dot': 'bounceDot 1.5s infinite',
//       },
//     },
//   },
//   plugins: [],
// };