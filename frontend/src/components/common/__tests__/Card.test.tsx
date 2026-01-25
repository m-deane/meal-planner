import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Card } from '../Card';

describe('Card', () => {
  it('renders children content', () => {
    render(<Card>Card content</Card>);
    expect(screen.getByText('Card content')).toBeInTheDocument();
  });

  it('renders header when provided', () => {
    render(<Card header={<h3>Card Header</h3>}>Content</Card>);
    expect(screen.getByText('Card Header')).toBeInTheDocument();
  });

  it('renders footer when provided', () => {
    render(<Card footer={<button>Action</button>}>Content</Card>);
    expect(screen.getByRole('button', { name: /action/i })).toBeInTheDocument();
  });

  it('renders image when provided', () => {
    render(
      <Card image={{ src: '/test.jpg', alt: 'Test image' }}>
        Content
      </Card>
    );
    const image = screen.getByRole('img', { name: /test image/i });
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('src', '/test.jpg');
  });

  it('applies correct aspect ratio classes to image', () => {
    const { rerender } = render(
      <Card image={{ src: '/test.jpg', alt: 'Test', aspectRatio: 'square' }}>
        Content
      </Card>
    );
    expect(screen.getByRole('img').parentElement).toHaveClass('aspect-square');

    rerender(
      <Card image={{ src: '/test.jpg', alt: 'Test', aspectRatio: 'video' }}>
        Content
      </Card>
    );
    expect(screen.getByRole('img').parentElement).toHaveClass('aspect-video');

    rerender(
      <Card image={{ src: '/test.jpg', alt: 'Test', aspectRatio: 'wide' }}>
        Content
      </Card>
    );
    expect(screen.getByRole('img').parentElement).toHaveClass('aspect-[21/9]');
  });

  it('applies hover classes when hoverable is true', () => {
    const { container } = render(<Card hoverable>Content</Card>);
    const card = container.firstChild as HTMLElement;
    expect(card).toHaveClass('hover:shadow-lg');
  });

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Card onClick={handleClick}>Content</Card>);
    const card = screen.getByRole('button');
    fireEvent.click(card);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('has role="button" when onClick is provided', () => {
    render(<Card onClick={vi.fn()}>Content</Card>);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('is keyboard accessible when clickable', () => {
    const handleClick = vi.fn();
    render(<Card onClick={handleClick}>Content</Card>);
    const card = screen.getByRole('button');

    fireEvent.keyDown(card, { key: 'Enter' });
    expect(handleClick).toHaveBeenCalledTimes(1);

    fireEvent.keyDown(card, { key: ' ' });
    expect(handleClick).toHaveBeenCalledTimes(2);
  });

  it('applies selected state correctly', () => {
    const { container } = render(<Card selected onClick={vi.fn()}>Content</Card>);
    const card = container.firstChild as HTMLElement;
    expect(card).toHaveClass('ring-2', 'ring-blue-500');
  });

  it('applies correct padding classes', () => {
    const { rerender } = render(<Card padding="none"><div data-testid="card-content">Content</div></Card>);
    let body = screen.getByTestId('card-content').parentElement!;
    expect(body).toHaveClass('p-0');

    rerender(<Card padding="sm"><div data-testid="card-content">Content</div></Card>);
    body = screen.getByTestId('card-content').parentElement!;
    expect(body).toHaveClass('p-3');

    rerender(<Card padding="md"><div data-testid="card-content">Content</div></Card>);
    body = screen.getByTestId('card-content').parentElement!;
    expect(body).toHaveClass('p-4');

    rerender(<Card padding="lg"><div data-testid="card-content">Content</div></Card>);
    body = screen.getByTestId('card-content').parentElement!;
    expect(body).toHaveClass('p-6');
  });

  it('applies custom className', () => {
    const { container } = render(<Card className="custom-class">Content</Card>);
    expect(container.firstChild).toHaveClass('custom-class');
  });
});
