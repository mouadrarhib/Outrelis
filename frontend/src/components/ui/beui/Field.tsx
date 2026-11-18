import type { InputHTMLAttributes, ReactNode, SelectHTMLAttributes } from 'react'

type FieldFrameProps = {
  id: string
  label: string
  hint?: string
  error?: string
  children: ReactNode
}

function FieldFrame({ id, label, hint, error, children }: FieldFrameProps) {
  return <div className="prospecting-field">
    <div className="prospecting-field-label">
      <label htmlFor={id}>{label}</label>
      {hint && <span>{hint}</span>}
    </div>
    {children}
    {error && <p className="prospecting-field-error" id={`${id}-error`}>{error}</p>}
  </div>
}

type TextFieldProps = Omit<InputHTMLAttributes<HTMLInputElement>, 'id'> & {
  id: string
  label: string
  hint?: string
  error?: string
}

export function TextField({ id, label, hint, error, className = '', ...props }: TextFieldProps) {
  return <FieldFrame id={id} label={label} hint={hint} error={error}>
    <input
      {...props}
      id={id}
      className={`prospecting-input ${className}`.trim()}
      aria-invalid={Boolean(error)}
      aria-describedby={error ? `${id}-error` : undefined}
    />
  </FieldFrame>
}

type SelectFieldProps = Omit<SelectHTMLAttributes<HTMLSelectElement>, 'id'> & {
  id: string
  label: string
  hint?: string
  error?: string
  children: ReactNode
}

export function SelectField({ id, label, hint, error, children, className = '', ...props }: SelectFieldProps) {
  return <FieldFrame id={id} label={label} hint={hint} error={error}>
    <span className="prospecting-select-wrap">
      <select
        {...props}
        id={id}
        className={`prospecting-input prospecting-select ${className}`.trim()}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? `${id}-error` : undefined}
      >
        {children}
      </select>
      <svg viewBox="0 0 20 20" aria-hidden="true"><path d="m6 8 4 4 4-4" /></svg>
    </span>
  </FieldFrame>
}
