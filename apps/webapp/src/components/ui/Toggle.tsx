interface ToggleProps {
  label: string;
  checked: boolean;
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'success' | 'warning' | 'danger';
  labels?: {
    on: string;
    off: string;
  };
  showLabels?: boolean;
  onChange: (checked: boolean) => void;
}

const sizeConfig = {
  sm: {
    label: 'text-xs',
    toggle: 'w-8 h-5',
    thumb: 'w-3 h-3',
    translate: 'translate-x-3',
    container: 'p-3'
  },
  md: {
    label: 'text-sm', 
    toggle: 'w-11 h-6',
    thumb: 'w-4 h-4',
    translate: 'translate-x-5',
    container: 'p-4'
  },
  lg: {
    label: 'text-base',
    toggle: 'w-14 h-7',
    thumb: 'w-5 h-5',
    translate: 'translate-x-7',
    container: 'p-5'
  }
};

const variantConfig = {
  default: {
    on: 'bg-blue-600',
    off: 'bg-gray-200',
    focus: 'focus:ring-blue-500'
  },
  success: {
    on: 'bg-green-600',
    off: 'bg-gray-200', 
    focus: 'focus:ring-green-500'
  },
  warning: {
    on: 'bg-yellow-500',
    off: 'bg-gray-200',
    focus: 'focus:ring-yellow-500'
  },
  danger: {
    on: 'bg-red-600',
    off: 'bg-gray-200',
    focus: 'focus:ring-red-500'
  }
};

export default function Toggle({
  label,
  checked,
  disabled = false,
  size = 'md',
  variant = 'default',
  labels = { on: 'On', off: 'Off' },
  showLabels = false,
  onChange
}: ToggleProps) {
  const sizeStyles = sizeConfig[size];
  const variantStyles = variantConfig[variant];

  const handleToggle = () => {
    if (!disabled) {
      onChange(!checked);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault();
      handleToggle();
    }
  };

  return (
    <div className={`bg-white ${sizeStyles.container} rounded-lg border`}>
      {/* Header */}
      <div className="flex justify-between items-center mb-3">
        <label className={`${sizeStyles.label} font-medium text-gray-700 uppercase tracking-wide`}>
          {label}
        </label>
        {showLabels && (
          <span className={`${sizeStyles.label} font-medium ${
            checked ? 'text-green-600' : 'text-gray-500'
          }`}>
            {checked ? labels.on : labels.off}
          </span>
        )}
      </div>

      {/* Toggle Switch */}
      <div className="flex items-center justify-center">
        <button
          type="button"
          role="switch"
          aria-checked={checked}
          aria-label={`Toggle ${label}`}
          disabled={disabled}
          onClick={handleToggle}
          onKeyDown={handleKeyDown}
          className={`
            ${sizeStyles.toggle} relative inline-flex items-center rounded-full
            transition-colors duration-200 ease-in-out
            ${checked ? variantStyles.on : variantStyles.off}
            ${disabled 
              ? 'cursor-not-allowed opacity-50' 
              : `cursor-pointer ${variantStyles.focus} focus:outline-none focus:ring-2 focus:ring-opacity-50`
            }
          `}
        >
          {/* Thumb */}
          <span
            className={`
              ${sizeStyles.thumb} inline-block bg-white rounded-full shadow-sm
              transition-transform duration-200 ease-in-out transform
              ${checked ? sizeStyles.translate : 'translate-x-1'}
            `}
          />
        </button>
      </div>

      {/* Status Text */}
      <div className="mt-3 text-center">
        <span className={`text-xs font-medium ${
          checked 
            ? variant === 'success' ? 'text-green-600' : 
              variant === 'warning' ? 'text-yellow-600' :
              variant === 'danger' ? 'text-red-600' : 'text-blue-600'
            : 'text-gray-400'
        }`}>
          {checked ? 'ACTIVE' : 'INACTIVE'}
        </span>
      </div>
    </div>
  );
}