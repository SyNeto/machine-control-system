interface SliderControlProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  unit?: string;
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
  showValue?: boolean;
  onChange: (value: number) => void;
  onChangeComplete?: (value: number) => void;
}

const sizeConfig = {
  sm: {
    label: 'text-xs',
    value: 'text-sm',
    container: 'p-3',
    slider: 'h-1'
  },
  md: {
    label: 'text-sm',
    value: 'text-base',
    container: 'p-4',
    slider: 'h-2'
  },
  lg: {
    label: 'text-base',
    value: 'text-lg',
    container: 'p-5',
    slider: 'h-3'
  }
};

export default function SliderControl({
  label,
  value,
  min,
  max,
  step = 1,
  unit,
  disabled = false,
  size = 'md',
  showValue = true,
  onChange,
  onChangeComplete
}: SliderControlProps) {
  const sizeStyles = sizeConfig[size];
  
  // Calculate percentage for styling
  const percentage = ((value - min) / (max - min)) * 100;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = Number(e.target.value);
    onChange(newValue);
  };

  const handleMouseUp = (e: React.MouseEvent<HTMLInputElement>) => {
    if (onChangeComplete) {
      const newValue = Number((e.target as HTMLInputElement).value);
      onChangeComplete(newValue);
    }
  };

  const formatValue = (val: number): string => {
    return val % 1 === 0 ? val.toString() : val.toFixed(2);
  };

  return (
    <div className={`bg-white ${sizeStyles.container} rounded-lg border`}>
      {/* Header */}
      <div className="flex justify-between items-center mb-3">
        <label className={`${sizeStyles.label} font-medium text-gray-700 uppercase tracking-wide`}>
          {label}
        </label>
        {showValue && (
          <div className="flex items-baseline gap-1">
            <span className={`${sizeStyles.value} font-bold text-gray-900 tabular-nums`}>
              {formatValue(value)}
            </span>
            {unit && (
              <span className="text-sm text-gray-500 font-medium">
                {unit}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Slider Container */}
      <div className="relative">
        {/* Background Track */}
        <div className={`${sizeStyles.slider} bg-gray-200 rounded-full relative overflow-hidden`}>
          {/* Progress Track */}
          <div 
            className={`${sizeStyles.slider} bg-blue-600 rounded-full transition-all duration-150 ease-out`}
            style={{ width: `${percentage}%` }}
          />
        </div>

        {/* Slider Input */}
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          disabled={disabled}
          onChange={handleChange}
          onMouseUp={handleMouseUp}
          onTouchEnd={(e) => handleMouseUp(e as any)}
          className={`
            absolute top-0 left-0 w-full ${sizeStyles.slider} opacity-0 cursor-pointer
            disabled:cursor-not-allowed disabled:opacity-50
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50
          `}
          aria-label={`${label} slider`}
        />

        {/* Thumb */}
        <div 
          className={`
            absolute top-1/2 transform -translate-y-1/2 -translate-x-1/2
            w-5 h-5 bg-white border-2 border-blue-600 rounded-full shadow-sm
            transition-all duration-150 ease-out
            ${disabled ? 'border-gray-400 bg-gray-100' : 'hover:scale-110'}
          `}
          style={{ left: `${percentage}%` }}
        />
      </div>

      {/* Range Labels */}
      <div className="flex justify-between mt-2">
        <span className="text-xs text-gray-400 font-medium">
          {formatValue(min)}{unit && ` ${unit}`}
        </span>
        <span className="text-xs text-gray-400 font-medium">
          {formatValue(max)}{unit && ` ${unit}`}
        </span>
      </div>
    </div>
  );
}