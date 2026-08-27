/**
 * STEP 8.1: PROFESSIONAL DESIGN SYSTEM
 * Enterprise-Grade Theme & Design Tokens
 * NSO/RBI Institutional Standards
 */

export const colors = {
  primary: {
    50: '#F0F4FA',
    100: '#D9E5F5',
    200: '#B8CEEB',
    300: '#8FB0DC',
    400: '#5F8FCC',
    500: '#2E5AA1', // Main institutional blue
    600: '#2447A8',
    700: '#1D3A8A',
    800: '#1E3A5F',
    900: '#162B47',
  },
  secondary: {
    50: '#FFF7ED',
    100: '#FFEDD5',
    200: '#FED7AA',
    300: '#FDBA74',
    400: '#FB923C',
    500: '#F97316', // Professional orange for CTAs
    600: '#EA580C',
    700: '#C2410C',
    800: '#9A3412',
    900: '#7C2D12',
  },
  success: {
    50: '#F0FDF4',
    100: '#DCFCE7',
    200: '#BBFBBB',
    300: '#86EFAC',
    400: '#4ADE80',
    500: '#22C55E', // Institutional green
    600: '#16A34A',
    700: '#15803D',
    800: '#166534',
    900: '#145231',
  },
  warning: {
    50: '#FFFBEB',
    100: '#FEF3C7',
    200: '#FDE68A',
    300: '#FCD34D',
    400: '#FBBF24',
    500: '#F59E0B',
    600: '#D97706',
    700: '#B45309',
    800: '#92400E',
    900: '#78350F',
  },
  danger: {
    50: '#FEF2F2',
    100: '#FEE2E2',
    200: '#FECACA',
    300: '#FCA5A5',
    400: '#F87171',
    500: '#EF4444',
    600: '#DC2626',
    700: '#B91C1C',
    800: '#991B1B',
    900: '#7F1D1D',
  },
  neutral: {
    50: '#FAFAFA',
    100: '#F5F5F5',
    200: '#E5E5E5',
    300: '#D4D4D4',
    400: '#A3A3A3',
    500: '#737373',
    600: '#525252',
    700: '#404040',
    800: '#262626',
    900: '#171717',
  },
  background: '#FAFAFA',
  surface: '#FFFFFF',
  border: '#E5E5E5',
  text: {
    primary: '#171717',
    secondary: '#525252',
    tertiary: '#A3A3A3',
  },
  dataViz: {
    blue: '#2E5AA1',
    orange: '#F97316',
    green: '#22C55E',
    red: '#EF4444',
    purple: '#A855F7',
    teal: '#14B8A6',
  },
};

export const typography = {
  fontFamily: {
    display: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    body: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    mono: '"Fira Code", "Courier New", monospace',
  },
  fontSize: {
    xs: '12px',
    sm: '13px',
    base: '14px',
    lg: '16px',
    xl: '18px',
    '2xl': '21px',
    '3xl': '24px',
    '4xl': '28px',
    '5xl': '32px',
  },
  lineHeight: {
    tight: '1.2',
    normal: '1.5',
    relaxed: '1.75',
    loose: '2',
  },
  fontWeight: {
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    extrabold: 800,
  },
  letterSpacing: {
    tight: '-0.02em',
    normal: '0',
    wide: '0.02em',
    wider: '0.05em',
  },
};

export const spacing = {
  0: '0',
  1: '4px',
  2: '8px',
  3: '12px',
  4: '16px',
  5: '20px',
  6: '24px',
  7: '28px',
  8: '32px',
  9: '36px',
  10: '40px',
  12: '48px',
  14: '56px',
  16: '64px',
  20: '80px',
  24: '96px',
};

export const borderRadius = {
  none: '0',
  sm: '4px',
  base: '6px',
  md: '8px',
  lg: '12px',
  xl: '16px',
  full: '9999px',
};

export const shadows = {
  none: 'none',
  xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
  base: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  md: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  lg: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  xl: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  hover: '0 20px 25px -5px rgba(0, 0, 0, 0.15), 0 10px 10px -5px rgba(0, 0, 0, 0.06)',
  focus: '0 0 0 3px rgba(46, 90, 161, 0.1)',
};

export const breakpoints = {
  xs: '320px',
  sm: '640px',
  md: '1024px',
  lg: '1280px',
  xl: '1536px',
  '2xl': '1920px',
};

export const transitions = {
  fast: '150ms cubic-bezier(0.4, 0, 0.2, 1)',
  base: '200ms cubic-bezier(0.4, 0, 0.2, 1)',
  slow: '300ms cubic-bezier(0.4, 0, 0.2, 1)',
  slowest: '500ms cubic-bezier(0.4, 0, 0.2, 1)',
};

export const semanticColors = {
  background: {
    primary: colors.background,
    secondary: colors.neutral[50],
    tertiary: colors.neutral[100],
  },
  text: {
    primary: colors.text.primary,
    secondary: colors.text.secondary,
    tertiary: colors.text.tertiary,
    inverse: colors.neutral[50],
  },
  border: {
    primary: colors.border,
    secondary: colors.neutral[200],
    focus: colors.primary[500],
  },
  status: {
    success: colors.success[500],
    warning: colors.warning[500],
    danger: colors.danger[500],
    info: colors.primary[500],
  },
  interaction: {
    background: colors.primary[500],
    backgroundHover: colors.primary[600],
    foreground: colors.neutral[50],
    disabled: colors.neutral[300],
  },
};

export const zIndex = {
  base: 0,
  dropdown: 100,
  sticky: 200,
  fixed: 300,
  backdrop: 400,
  modal: 500,
  popover: 600,
  tooltip: 700,
};

export const theme = {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  breakpoints,
  transitions,
  semanticColors,
  zIndex,
};

export default theme;