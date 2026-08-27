/**
 * STEP 8.3: PROFESSIONAL REACT COMPONENT LIBRARY
 * Enterprise-Grade Base Components
 * No Templates, Pure Professional Design Implementation
 */

import React, { forwardRef, useState, useCallback } from 'react';
import styled from 'styled-components';
import { theme } from '../theme/designSystem';

// ============ BUTTON COMPONENT ============

const StyledButton = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: ${theme.typography.fontFamily.body};
  font-size: ${theme.typography.fontSize.sm};
  font-weight: ${theme.typography.fontWeight.medium};
  padding: ${theme.spacing[3]} ${theme.spacing[4]};
  border: none;
  border-radius: ${theme.borderRadius.base};
  cursor: pointer;
  transition: all ${theme.transitions.base};
  gap: ${theme.spacing[2]};
  white-space: nowrap;
  user-select: none;

  /* Primary variant */
  ${props => props.variant === 'primary' && `
    background-color: ${theme.colors.primary[500]};
    color: white;

    &:hover:not(:disabled) {
      background-color: ${theme.colors.primary[600]};
      box-shadow: ${theme.shadows.hover};
    }

    &:active:not(:disabled) {
      transform: translateY(1px);
    }
  `}

  /* Secondary variant */
  ${props => props.variant === 'secondary' && `
    background-color: ${theme.colors.neutral[100]};
    color: ${theme.colors.text.primary};
    border: 1px solid ${theme.colors.border};

    &:hover:not(:disabled) {
      background-color: ${theme.colors.neutral[200]};
      border-color: ${theme.colors.border};
    }
  `}

  /* Tertiary variant */
  ${props => props.variant === 'tertiary' && `
    background-color: transparent;
    color: ${theme.colors.primary[500]};
    border: 1px solid ${theme.colors.primary[200]};

    &:hover:not(:disabled) {
      background-color: ${theme.colors.primary[50]};
      border-color: ${theme.colors.primary[300]};
    }
  `}

  /* Danger variant */
  ${props => props.variant === 'danger' && `
    background-color: ${theme.colors.danger[500]};
    color: white;

    &:hover:not(:disabled) {
      background-color: ${theme.colors.danger[600]};
    }
  `}

  /* Success variant */
  ${props => props.variant === 'success' && `
    background-color: ${theme.colors.success[500]};
    color: white;

    &:hover:not(:disabled) {
      background-color: ${theme.colors.success[600]};
    }
  `}

  /* Size variants */
  ${props => props.size === 'sm' && `
    padding: ${theme.spacing[2]} ${theme.spacing[3]};
    font-size: ${theme.typography.fontSize.xs};
  `}

  ${props => props.size === 'lg' && `
    padding: ${theme.spacing[4]} ${theme.spacing[6]};
    font-size: ${theme.typography.fontSize.base};
  `}

  /* Disabled state */
  &:disabled {
    background-color: ${theme.colors.neutral[200]};
    color: ${theme.colors.neutral[400]};
    cursor: not-allowed;
    opacity: 0.6;
  }

  /* Focus state */
  &:focus-visible {
    outline: 2px solid ${theme.colors.primary[500]};
    outline-offset: 2px;
  }

  /* Loading state */
  ${props => props.isLoading && `
    position: relative;
    color: transparent;

    &::after {
      content: '';
      position: absolute;
      width: 16px;
      height: 16px;
      top: 50%;
      left: 50%;
      margin-left: -8px;
      margin-top: -8px;
      border: 2px solid currentColor;
      border-right-color: transparent;
      border-radius: 50%;
      animation: spin 0.6s linear infinite;
    }
  `}
`;

export const Button = forwardRef(
  ({ children, variant = 'primary', size = 'base', isLoading = false, ...props }, ref) => (
    <StyledButton
      ref={ref}
      variant={variant}
      size={size}
      isLoading={isLoading}
      disabled={isLoading || props.disabled}
      {...props}
    >
      {children}
    </StyledButton>
  )
);

Button.displayName = 'Button';

// ============ CARD COMPONENT ============

const StyledCard = styled.div`
  background-color: ${theme.semanticColors.background.primary};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  box-shadow: ${theme.shadows.sm};
  transition: all ${theme.transitions.base};

  ${props => props.hoverable && `
    cursor: pointer;

    &:hover {
      box-shadow: ${theme.shadows.hover};
      border-color: ${theme.colors.primary[200]};
    }
  `}

  ${props => props.interactive && `
    &:active {
      transform: translateY(2px);
      box-shadow: ${theme.shadows.base};
    }
  `}
`;

const CardHeader = styled.div`
  padding: ${theme.spacing[6]};
  border-bottom: 1px solid ${theme.colors.border};
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const CardTitle = styled.h3`
  font-size: ${theme.typography.fontSize['2xl']};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text.primary};
  margin: 0;
`;

const CardContent = styled.div`
  padding: ${theme.spacing[6]};
`;

const CardFooter = styled.div`
  padding: ${theme.spacing[6]};
  border-top: 1px solid ${theme.colors.border};
  display: flex;
  justify-content: flex-end;
  gap: ${theme.spacing[3]};
`;

export const Card = ({ children, header, title, footer, ...props }) => (
  <StyledCard {...props}>
    {header && <CardHeader>{header}</CardHeader>}
    {title && !header && <CardHeader><CardTitle>{title}</CardTitle></CardHeader>}
    <CardContent>{children}</CardContent>
    {footer && <CardFooter>{footer}</CardFooter>}
  </StyledCard>
);

// ============ INPUT COMPONENT ============

const InputWrapper = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing[2]};
`;

const InputLabel = styled.label`
  font-size: ${theme.typography.fontSize.sm};
  font-weight: ${theme.typography.fontWeight.medium};
  color: ${theme.colors.text.primary};
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const StyledInput = styled.input`
  padding: ${theme.spacing[3]} ${theme.spacing[4]};
  font-size: ${theme.typography.fontSize.base};
  font-family: ${theme.typography.fontFamily.body};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.base};
  background-color: ${theme.colors.surface};
  color: ${theme.colors.text.primary};
  transition: all ${theme.transitions.base};

  &:hover {
    border-color: ${theme.colors.primary[300]};
  }

  &:focus {
    outline: none;
    border-color: ${theme.colors.primary[500]};
    box-shadow: ${theme.shadows.focus};
  }

  &::placeholder {
    color: ${theme.colors.text.tertiary};
  }

  &:disabled {
    background-color: ${theme.colors.neutral[100]};
    color: ${theme.colors.text.tertiary};
    cursor: not-allowed;
  }

  ${props => props.error && `
    border-color: ${theme.colors.danger[500]};
    
    &:focus {
      box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
    }
  `}

  /* Size variants */
  ${props => props.size === 'sm' && `
    padding: ${theme.spacing[2]} ${theme.spacing[3]};
    font-size: ${theme.typography.fontSize.sm};
  `}

  ${props => props.size === 'lg' && `
    padding: ${theme.spacing[4]} ${theme.spacing[4]};
    font-size: ${theme.typography.fontSize.lg};
  `}
`;

const ErrorMessage = styled.span`
  font-size: ${theme.typography.fontSize.xs};
  color: ${theme.colors.danger[500]};
  margin-top: ${theme.spacing[1]};
`;

const HelperText = styled.span`
  font-size: ${theme.typography.fontSize.xs};
  color: ${theme.colors.text.tertiary};
  margin-top: ${theme.spacing[1]};
`;

export const Input = forwardRef(
  ({ label, error, helperText, size = 'base', ...props }, ref) => (
    <InputWrapper>
      {label && <InputLabel>{label}</InputLabel>}
      <StyledInput ref={ref} error={error} size={size} {...props} />
      {error && <ErrorMessage>{error}</ErrorMessage>}
      {helperText && !error && <HelperText>{helperText}</HelperText>}
    </InputWrapper>
  )
);

Input.displayName = 'Input';

// ============ BADGE COMPONENT ============

const StyledBadge = styled.span`
  display: inline-flex;
  align-items: center;
  gap: ${theme.spacing[1]};
  font-size: ${theme.typography.fontSize.xs};
  font-weight: ${theme.typography.fontWeight.medium};
  padding: ${theme.spacing[1]} ${theme.spacing[2]};
  border-radius: ${theme.borderRadius.full};
  white-space: nowrap;

  /* Variant: Success */
  ${props => props.variant === 'success' && `
    background-color: ${theme.colors.success[50]};
    color: ${theme.colors.success[700]};
  `}

  /* Variant: Warning */
  ${props => props.variant === 'warning' && `
    background-color: ${theme.colors.warning[50]};
    color: ${theme.colors.warning[700]};
  `}

  /* Variant: Danger */
  ${props => props.variant === 'danger' && `
    background-color: ${theme.colors.danger[50]};
    color: ${theme.colors.danger[700]};
  `}

  /* Variant: Info */
  ${props => props.variant === 'info' && `
    background-color: ${theme.colors.primary[50]};
    color: ${theme.colors.primary[700]};
  `}

  /* Variant: Neutral */
  ${props => props.variant === 'neutral' && `
    background-color: ${theme.colors.neutral[100]};
    color: ${theme.colors.neutral[700]};
  `}
`;

export const Badge = ({ children, variant = 'neutral' }) => (
  <StyledBadge variant={variant}>{children}</StyledBadge>
);

// ============ STAT CARD COMPONENT ============

const StatCardContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing[2]};
`;

const StatLabel = styled.span`
  font-size: ${theme.typography.fontSize.sm};
  font-weight: ${theme.typography.fontWeight.medium};
  color: ${theme.colors.text.secondary};
  text-transform: uppercase;
  letter-spacing: 0.05em;
`;

const StatValue = styled.div`
  font-size: ${theme.typography.fontSize['4xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.text.primary};
  line-height: 1;
`;

const StatChange = styled.div`
  font-size: ${theme.typography.fontSize.sm};
  font-weight: ${theme.typography.fontWeight.medium};
  display: flex;
  align-items: center;
  gap: ${theme.spacing[1]};

  ${props => props.positive && `
    color: ${theme.colors.success[600]};
  `}

  ${props => !props.positive && props.negative && `
    color: ${theme.colors.danger[600]};
  `}
`;

export const StatCard = ({ label, value, change, changeLabel, ...props }) => (
  <Card {...props}>
    <StatCardContainer>
      <StatLabel>{label}</StatLabel>
      <StatValue>{value}</StatValue>
      {change !== undefined && (
        <StatChange positive={change >= 0} negative={change < 0}>
          <span>{change >= 0 ? '↑' : '↓'} {Math.abs(change)}%</span>
          {changeLabel && <span>{changeLabel}</span>}
        </StatChange>
      )}
    </StatCardContainer>
  </Card>
);

// ============ LOADING SPINNER ============

const SpinnerContainer = styled.div`
  display: inline-flex;
  align-items: center;
  justify-content: center;

  ${props => props.size === 'sm' && `
    width: 20px;
    height: 20px;
  `}

  ${props => props.size === 'base' && `
    width: 40px;
    height: 40px;
  `}

  ${props => props.size === 'lg' && `
    width: 60px;
    height: 60px;
  `}
`;

const SpinnerSVG = styled.svg`
  animation: spin 0.8s linear infinite;

  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
`;

export const Spinner = ({ size = 'base', color = 'primary' }) => {
  const sizeMap = { sm: 20, base: 40, lg: 60 };
  const dimension = sizeMap[size];
  const colorValue = theme.colors[color]?.[500] || theme.colors.primary[500];

  return (
    <SpinnerContainer size={size}>
      <SpinnerSVG width={dimension} height={dimension} viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="10" stroke={colorValue} strokeWidth="2" opacity="0.25" />
        <path
          d="M12 2A10 10 0 0 1 22 12"
          stroke={colorValue}
          strokeWidth="2"
          strokeLinecap="round"
        />
      </SpinnerSVG>
    </SpinnerContainer>
  );
};

// ============ ALERT COMPONENT ============

const AlertContainer = styled.div`
  display: flex;
  gap: ${theme.spacing[4]};
  padding: ${theme.spacing[4]};
  border-radius: ${theme.borderRadius.md};
  border: 1px solid;

  ${props => props.type === 'success' && `
    background-color: ${theme.colors.success[50]};
    border-color: ${theme.colors.success[200]};
    color: ${theme.colors.success[800]};
  `}

  ${props => props.type === 'warning' && `
    background-color: ${theme.colors.warning[50]};
    border-color: ${theme.colors.warning[200]};
    color: ${theme.colors.warning[800]};
  `}

  ${props => props.type === 'danger' && `
    background-color: ${theme.colors.danger[50]};
    border-color: ${theme.colors.danger[200]};
    color: ${theme.colors.danger[800]};
  `}

  ${props => props.type === 'info' && `
    background-color: ${theme.colors.primary[50]};
    border-color: ${theme.colors.primary[200]};
    color: ${theme.colors.primary[800]};
  `}
`;

const AlertIcon = styled.div`
  display: flex;
  align-items: flex-start;
  font-size: 20px;
`;

const AlertContent = styled.div`
  flex: 1;
`;

export const Alert = ({ type = 'info', title, children, closeable = false, onClose }) => {
  const [isOpen, setIsOpen] = useState(true);

  const handleClose = useCallback(() => {
    setIsOpen(false);
    onClose?.();
  }, [onClose]);

  if (!isOpen) return null;

  const iconMap = {
    success: '✓',
    warning: '⚠',
    danger: '✕',
    info: 'ℹ',
  };

  return (
    <AlertContainer type={type}>
      <AlertIcon>{iconMap[type]}</AlertIcon>
      <AlertContent>
        {title && <strong>{title}</strong>}
        {children}
      </AlertContent>
      {closeable && (
        <Button variant="tertiary" size="sm" onClick={handleClose}>
          ✕
        </Button>
      )}
    </AlertContainer>
  );
};

export default {
  Button,
  Card,
  Input,
  Badge,
  StatCard,
  Spinner,
  Alert,
};