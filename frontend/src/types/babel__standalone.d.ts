declare module '@babel/standalone' {
  export interface TransformResult {
    code: string;
    map: any;
    ast: any;
  }

  export interface TransformOptions {
    filename?: string;
    presets?: string[];
    plugins?: string[];
    configFile?: boolean;
    babelrc?: boolean;
  }

  export function transform(code: string, options?: TransformOptions): TransformResult;
  
  export const availablePresets: {
    [key: string]: any;
  };
} 