import { Typography } from "antd";

const { Text } = Typography;

type LogoLockupProps = {
  subtitle?: string;
  size?: "sm" | "md" | "lg";
  className?: string;
};

export const LogoLockup = ({
  subtitle = "Transport Service UAE",
  size = "md",
  className = "",
}: LogoLockupProps) => {
  return (
    <div className={`logo-lockup logo-${size} ${className}`.trim()}>
      <div className="logo-mark-wrap" aria-hidden="true">
        <span className="logo-mark-dot" />
        <svg viewBox="0 0 24 24" className="logo-mark-svg">
          <path d="M2 16l2.4-2.4h4.2l2.5 2.4h4.2l2.5-2.4H22" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" />
          <path d="M4.4 13.6V7.7a2 2 0 0 1 2-2h10.2a2 2 0 0 1 2 2v5.9" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" />
          <path d="M8.6 10.2h6.8M12 5.7v7.9" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </div>
      <div className="logo-copy">
        <Text strong>Sikar Cargo</Text>
        <Text>{subtitle}</Text>
      </div>
    </div>
  );
};
