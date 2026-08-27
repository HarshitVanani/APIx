/**
 * STEP 8.5: INSTITUTIONAL HEADER & AUDIT CONTROLS
 * MoSPI / RBI / NSO Official Submission Workflow
 */

import React from 'react';
import styled from 'styled-components';
import { Plane, RefreshCw, Send, Download, ShieldCheck } from 'lucide-react';
import { theme } from '../theme/designSystem';
import { Button, Badge } from './BaseComponents';

const HeaderContainer = styled.header`
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: ${theme.spacing[6]};
  border-bottom: 1px solid ${theme.colors.border};
  gap: ${theme.spacing[4]};

  @media (min-width: ${theme.breakpoints.md}) {
    flex-direction: row;
    align-items: center;
  }
`;

const BrandingBlock = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing[3]};
`;

const IconWrapper = styled.div`
  padding: ${theme.spacing[3]};
  background-color: ${theme.colors.primary[50]};
  border: 1px solid ${theme.colors.primary[200]};
  border-radius: ${theme.borderRadius.lg};
  color: ${theme.colors.primary[500]};
  display: flex;
  align-items: center;
  justify-content: center;
`;

const ControlsGroup = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing[3]};
  flex-wrap: wrap;
`;

export const InstitutionalHeader = ({
  onRefresh,
  onSubmitNso,
  onExportCsv,
  isLoading,
  nsoStatus
}) => {
  return (
    <HeaderContainer>
      <BrandingBlock>
        <IconWrapper>
          <Plane size={26} />
        </IconWrapper>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing[2] }}>
            <h1 style={{ margin: 0, fontSize: theme.typography.fontSize['3xl'], fontWeight: theme.typography.fontWeight.bold }}>
              APIx
            </h1>
            <Badge variant="info">SIH 2026 • PS 26056</Badge>
          </div>
          <p style={{ margin: 0, fontSize: theme.typography.fontSize.xs, color: theme.colors.text.secondary }}>
            MoSPI / NSO — Real-Time Airfare Price Index & CPI Augmentation Engine
          </p>
        </div>
      </BrandingBlock>

      <ControlsGroup>
        <Button
          variant="primary"
          size="sm"
          onClick={onSubmitNso}
          disabled={nsoStatus === 'submitting'}
          isLoading={nsoStatus === 'submitting'}
        >
          <Send size={14} />
          {nsoStatus === 'success' ? 'Submitted to MoSPI (Ref #2026)' : 'Submit to MoSPI Feed'}
        </Button>

        <Button variant="secondary" size="sm" onClick={onExportCsv}>
          <Download size={14} /> Export CSV
        </Button>

        <Button variant="secondary" size="sm" onClick={onRefresh} disabled={isLoading}>
          <RefreshCw size={14} className={isLoading ? 'animate-spin' : ''} />
          Refresh
        </Button>

        <Badge variant="success">
          <ShieldCheck size={12} /> DGCA FEED ACTIVE
        </Badge>
      </ControlsGroup>
    </HeaderContainer>
  );
};

export default InstitutionalHeader;