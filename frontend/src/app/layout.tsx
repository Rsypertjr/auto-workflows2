import type { Metadata } from 'next';
//import './globals.css'; // Remove this line if you don't have a globals.css file yet

export const metadata: Metadata = {
  title: 'Production System Dashboard',
  description: 'Automated Operations Monitor',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
