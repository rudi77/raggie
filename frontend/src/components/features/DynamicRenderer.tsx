'use client'

import React, { useEffect, useState } from 'react'
import * as Babel from '@babel/standalone'

export default function DynamicRenderer() {
  const [DynamicComponent, setDynamicComponent] = useState<React.FC | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchAndTransform = async () => {
      try {
        console.log('Fetching code from backend...')
        const response = await fetch('/api/generated-code')
        if (!response.ok) {
          throw new Error('Failed to fetch code')
        }
        
        const data = await response.json()
        console.log('Received code:', data.code)
        
        // Transform the code using Babel with proper preset configuration
        console.log('Transforming code with Babel...')
        const transformed = Babel.transform(data.code, {
          presets: [Babel.availablePresets['react']],
          filename: 'dynamic.js',
          configFile: false,
          babelrc: false,
        }).code
        console.log('Transformed code:', transformed)

        // Create a new function to evaluate the code in the proper context
        const moduleCode = `
          const React = arguments[0];
          const exports = {};
          ${transformed}
          return exports.default;
        `
        console.log('Executing code with context...')
        const executeCode = new Function(moduleCode)

        // Execute the code with React in context
        const Component = executeCode(React)
        console.log('Component created:', Component)
        
        if (typeof Component !== 'function') {
          throw new Error('Generated code did not return a valid React component')
        }

        setDynamicComponent(() => Component)
        setError(null)
      } catch (err) {
        console.error('Error in DynamicRenderer:', err)
        setError(err instanceof Error ? err.message : 'Failed to render component')
      }
    }

    fetchAndTransform()
  }, [])

  if (error) {
    return (
      <div className="bg-[#1a2634] rounded-lg p-4">
        <div className="text-red-500">Error: {error}</div>
      </div>
    )
  }

  return (
    <div className="bg-[#1a2634] rounded-lg p-4">
      {DynamicComponent ? (
        <DynamicComponent />
      ) : (
        <div className="text-secondary">Loading component...</div>
      )}
    </div>
  )
} 