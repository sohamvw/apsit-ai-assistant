export const metadata = {
  title: "APSIT AI Assistant",
  description: "Official APSIT AI Chatbot"
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body style={{ margin: 0 }}>
        {children}
      </body>
    </html>
  );
}
