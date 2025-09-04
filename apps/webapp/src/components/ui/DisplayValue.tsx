interface DisplayValueProps {
  label: string;
  value: string | number;
  unit?: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'highlighted' | 'muted';
  icon?: React.ReactNode;
  loading?: boolean;
}

const sizeConfig = {
  sm: {
    label: 'text-xs',
    value: 'text-lg',
    unit: 'text-xs',
    container: 'p-2'
  },
  md: {
    label: 'text-sm',
    value: 'text-2xl',
    unit: 'text-sm',
    container: 'p-3'
  },
  lg: {
    label: 'text-base',
    value: 'text-3xl',
    unit: 'text-base',
    container: 'p-4'
  }
};

const variantConfig = {
  default: {
    label: 'text-gray-600',
    value: 'text-gray-900',
    unit: 'text-gray-500',
    bg: 'bg-gray-50'
  },
  highlighted: {
    label: 'text-blue-600',
    value: 'text-blue-900',
    unit: 'text-blue-500',
    bg: 'bg-blue-50'
  },
  muted: {
    label: 'text-gray-400',
    value: 'text-gray-600',
    unit: 'text-gray-400',
    bg: 'bg-gray-25'
  }
};

export default function DisplayValue({
  label,
  value,
  unit,
  size = 'md',
  variant = 'default',
  icon,
  loading = false
}: DisplayValueProps) {
  const sizeStyles = sizeConfig[size];
  const variantStyles = variantConfig[variant];

  const formatValue = (val: string | number): string => {
    if (typeof val === 'number') {
      // Format numbers with appropriate decimals
      return val % 1 === 0 ? val.toString() : val.toFixed(2);
    }
    return val;
  };

  return (
    <div className={`${variantStyles.bg} ${sizeStyles.container} rounded-lg border`}>
      {/* Label with optional icon */}
      <div className="flex items-center gap-2 mb-1">
        {icon && (
          <div className={`${variantStyles.label} flex-shrink-0`}>
            {icon}
          </div>
        )}
        <span className={`${variantStyles.label} ${sizeStyles.label} font-medium uppercase tracking-wide`}>
          {label}
        </span>
      </div>

      {/* Value display */}
      <div className="flex items-baseline gap-2">
        {loading ? (
          <div className="flex items-center gap-2">
            <div className="animate-spin w-4 h-4 border-2 border-gray-300 border-t-blue-600 rounded-full" />
            <span className={`${variantStyles.value} ${sizeStyles.value} font-bold`}>
              --
            </span>
          </div>
        ) : (
          <>
            <span className={`${variantStyles.value} ${sizeStyles.value} font-bold tabular-nums`}>
              {formatValue(value)}
            </span>
            {unit && (
              <span className={`${variantStyles.unit} ${sizeStyles.unit} font-medium`}>
                {unit}
              </span>
            )}
          </>
        )}
      </div>
    </div>
  );
}