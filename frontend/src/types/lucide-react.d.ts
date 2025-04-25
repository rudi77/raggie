declare module 'lucide-react' {
  import * as React from 'react';

  export interface IconProps extends React.SVGProps<SVGSVGElement> {
    size?: number | string;
    color?: string;
    strokeWidth?: number | string;
  }

  export const Sun: React.FC<IconProps>;
  export const Moon: React.FC<IconProps>;
  export const Paperclip: React.FC<IconProps>;
  export const Mic: React.FC<IconProps>;
  export const Send: React.FC<IconProps>;
} 