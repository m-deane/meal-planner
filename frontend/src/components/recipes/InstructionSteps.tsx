import React, { useState } from 'react';
import { ClockIcon, ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline';
import { CheckCircleIcon } from '@heroicons/react/24/solid';
import type { Instruction } from '../../types';

/**
 * InstructionSteps component props
 */
export interface InstructionStepsProps {
  /**
   * Array of cooking instructions
   */
  instructions: Instruction[];

  /**
   * Whether steps can be expanded/collapsed for more details
   * @default false
   */
  expandable?: boolean;

  /**
   * Whether to show checkboxes for marking steps as complete
   * @default true
   */
  showCheckboxes?: boolean;

  /**
   * Callback when a step is marked complete/incomplete
   */
  onStepToggle?: (stepNumber: number, completed: boolean) => void;

  /**
   * Set of step numbers that are completed
   */
  completedSteps?: Set<number>;

  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Individual instruction step component
 */
interface InstructionStepProps {
  instruction: Instruction;
  expandable: boolean;
  showCheckbox: boolean;
  completed: boolean;
  onToggle: (completed: boolean) => void;
}

const InstructionStep: React.FC<InstructionStepProps> = ({
  instruction,
  expandable,
  showCheckbox,
  completed,
  onToggle,
}) => {
  const [isExpanded, setIsExpanded] = useState(!expandable);

  const toggleExpanded = () => {
    if (expandable) {
      setIsExpanded(!isExpanded);
    }
  };

  const handleCheckboxClick = () => {
    onToggle(!completed);
  };

  // Truncate instruction text for collapsed state
  const shouldTruncate = expandable && !isExpanded && instruction.instruction.length > 150;
  const displayText = shouldTruncate
    ? `${instruction.instruction.substring(0, 150)}...`
    : instruction.instruction;

  return (
    <li className="flex gap-4">
      {/* Step number badge */}
      <div className="flex-shrink-0">
        <div
          className={`
            flex items-center justify-center w-8 h-8 rounded-full font-semibold text-sm
            ${
              completed
                ? 'bg-green-100 text-green-800'
                : 'bg-blue-100 text-blue-800'
            }
          `}
        >
          {completed ? (
            <CheckCircleIcon className="h-5 w-5 text-green-600" aria-hidden="true" />
          ) : (
            instruction.step_number
          )}
        </div>
      </div>

      {/* Step content */}
      <div className="flex-1 pb-8 last:pb-0">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <p
              className={`text-gray-900 leading-relaxed ${
                completed ? 'line-through text-gray-500' : ''
              }`}
            >
              {displayText}
            </p>

            {instruction.time_minutes !== null && instruction.time_minutes > 0 && (
              <div className="flex items-center gap-1 mt-2 text-sm text-gray-600">
                <ClockIcon className="h-4 w-4" aria-hidden="true" />
                <span>{instruction.time_minutes} min</span>
              </div>
            )}

            {/* Expand/collapse button */}
            {expandable && instruction.instruction.length > 150 && (
              <button
                type="button"
                onClick={toggleExpanded}
                className="mt-2 flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded px-1"
              >
                {isExpanded ? (
                  <>
                    <ChevronUpIcon className="h-4 w-4" aria-hidden="true" />
                    Show less
                  </>
                ) : (
                  <>
                    <ChevronDownIcon className="h-4 w-4" aria-hidden="true" />
                    Show more
                  </>
                )}
              </button>
            )}
          </div>

          {/* Checkbox */}
          {showCheckbox && (
            <button
              type="button"
              onClick={handleCheckboxClick}
              className={`
                flex-shrink-0 mt-1 px-3 py-1 rounded-md text-sm font-medium transition-colors
                focus:outline-none focus:ring-2 focus:ring-blue-500
                ${
                  completed
                    ? 'bg-green-100 text-green-800 hover:bg-green-200'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }
              `}
              aria-label={`Mark step ${instruction.step_number} as ${
                completed ? 'incomplete' : 'complete'
              }`}
            >
              {completed ? 'Done' : 'Mark done'}
            </button>
          )}
        </div>
      </div>
    </li>
  );
};

/**
 * InstructionSteps component
 *
 * Displays numbered cooking instruction steps with optional checkboxes,
 * time estimates, and expandable details.
 *
 * @example
 * ```tsx
 * <InstructionSteps
 *   instructions={recipe.instructions}
 *   showCheckboxes
 *   expandable
 *   onStepToggle={(stepNumber, completed) => console.log(stepNumber, completed)}
 * />
 * ```
 */
export const InstructionSteps: React.FC<InstructionStepsProps> = ({
  instructions,
  expandable = false,
  showCheckboxes = true,
  onStepToggle,
  completedSteps = new Set(),
  className = '',
}) => {
  const [internalCompleted, setInternalCompleted] = useState<Set<number>>(completedSteps);

  const handleToggle = (stepNumber: number, completed: boolean) => {
    const newCompleted = new Set(internalCompleted);
    if (completed) {
      newCompleted.add(stepNumber);
    } else {
      newCompleted.delete(stepNumber);
    }
    setInternalCompleted(newCompleted);
    onStepToggle?.(stepNumber, completed);
  };

  // Sort instructions by step_number
  const sortedInstructions = [...instructions].sort(
    (a, b) => a.step_number - b.step_number
  );

  // Calculate total time
  const totalTime = sortedInstructions.reduce(
    (sum, instruction) => sum + (instruction.time_minutes || 0),
    0
  );

  return (
    <div className={className}>
      {totalTime > 0 && (
        <div className="mb-4 flex items-center gap-2 text-sm text-gray-600 bg-gray-50 px-4 py-2 rounded-lg">
          <ClockIcon className="h-5 w-5" aria-hidden="true" />
          <span className="font-medium">Total cooking time: {totalTime} minutes</span>
        </div>
      )}

      <ol className="relative border-l-2 border-gray-200 ml-4 space-y-0">
        {sortedInstructions.map((instruction) => (
          <InstructionStep
            key={instruction.step_number}
            instruction={instruction}
            expandable={expandable}
            showCheckbox={showCheckboxes}
            completed={internalCompleted.has(instruction.step_number)}
            onToggle={(completed) => handleToggle(instruction.step_number, completed)}
          />
        ))}
      </ol>
    </div>
  );
};

export default InstructionSteps;
