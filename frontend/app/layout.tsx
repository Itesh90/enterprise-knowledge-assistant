import '../styles/globals.css';
import { Providers } from './providers';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head />
      <body className="min-h-screen">
        <Providers>
          <div className="container mx-auto p-4">{children}</div>
        </Providers>
      </body>
    </html>
  );
}


