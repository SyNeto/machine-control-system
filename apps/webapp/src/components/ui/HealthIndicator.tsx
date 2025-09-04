interface HealthIndicatorProps {
  status: 'online' | 'offline' | 'error' | 'warning';
  label?: string;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const statusConfig = {
  online: {
    color: 'bg-green-400',
    textColor: 'text-green-600',
    label: 'Online',
    icon: '●'
  },
  offline: {
    color: 'bg-gray-400',
    textColor: 'text-gray-600', 
    label: 'Offline',
    icon: '●'
  },
  error: {
    color: 'bg-red-400',
    textColor: 'text-red-600',
    label: 'Error',
    icon: '⚠'
  },
  warning: {
    color: 'bg-yellow-400',
    textColor: 'text-yellow-600',
    label: 'Warning',
    icon: '⚠'
  }
};

const sizeConfig = {
  sm: {
    dot: 'w-2 h-2',
    text: 'text-xs',
    container: 'gap-1'
  },
  md: {
    dot: 'w-3 h-3', 
    text: 'text-sm',
    container: 'gap-2'
  },
  lg: {
    dot: 'w-4 h-4',
    text: 'text-base',
    container: 'gap-2'
  }
};

export default function HealthIndicator({ 
  status, 
  label,
  showLabel = true,
  size = 'md' 
}: HealthIndicatorProps) {
  const config = statusConfig[status];
  const sizeStyles = sizeConfig[size];
  const displayLabel = label || config.label;

  return (
    <div className={`flex items-center ${sizeStyles.container}`}>
      {/* Status Dot */}
      <div 
        className={`${config.color} ${sizeStyles.dot} rounded-full animate-pulse`}
        title={displayLabel}
        aria-label={`Status: ${displayLabel}`}
      />
      
      {/* Optional Label */}
      {showLabel && (
        <span className={`${config.textColor} ${sizeStyles.text} font-medium`}>
          {displayLabel}
        </span>
      )}
    </div>
  );
}