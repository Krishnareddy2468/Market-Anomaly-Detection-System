export default function TestPage() {
  return (
    <div className="p-8 bg-background text-foreground min-h-screen">
      <h1 className="text-4xl font-bold mb-4">Test Page</h1>
      <div className="bg-card p-4 rounded-lg border border-border">
        <p className="text-foreground">If you can see this, the app is rendering correctly.</p>
        <ul className="list-disc list-inside mt-4 space-y-2 text-sm">
          <li>Background color is set</li>
          <li>Text color is set</li>
          <li>Card styling is working</li>
          <li>Typography is applied</li>
        </ul>
      </div>
      <a href="/" className="mt-4 inline-block text-accent hover:underline">Back to Dashboard</a>
    </div>
  )
}
