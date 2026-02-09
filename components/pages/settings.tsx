'use client'

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Switch } from '@/components/ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

export function SettingsPage() {
  return (
    <div className="p-6 space-y-6 ml-20 md:ml-64">
      {/* User Settings */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-primary">Profile Settings</CardTitle>
          <CardDescription>Manage your account information</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-foreground mb-2 block">First Name</label>
              <Input placeholder="John" className="bg-input border-border" />
            </div>
            <div>
              <label className="text-sm font-medium text-foreground mb-2 block">Last Name</label>
              <Input placeholder="Smith" className="bg-input border-border" />
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-foreground mb-2 block">Email Address</label>
            <Input placeholder="john.smith@company.com" type="email" className="bg-input border-border" />
          </div>
          <Button className="bg-primary hover:bg-primary/90 text-primary-foreground">Save Changes</Button>
        </CardContent>
      </Card>

      {/* Alert Thresholds */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-primary">Alert Configuration</CardTitle>
          <CardDescription>Configure alert thresholds and sensitivity</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium text-foreground mb-2 block">High-Risk Threshold</label>
            <Input placeholder="85" type="number" className="bg-input border-border" />
            <p className="text-xs text-muted-foreground mt-1">Alerts above this score are marked as High</p>
          </div>
          <div>
            <label className="text-sm font-medium text-foreground mb-2 block">Medium-Risk Threshold</label>
            <Input placeholder="50" type="number" className="bg-input border-border" />
            <p className="text-xs text-muted-foreground mt-1">Alerts between this and High threshold are Medium</p>
          </div>
          <Button className="bg-primary hover:bg-primary/90 text-primary-foreground">Update Thresholds</Button>
        </CardContent>
      </Card>

      {/* Notification Preferences */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-primary">Notifications</CardTitle>
          <CardDescription>Manage how you receive alerts and updates</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-foreground">High-Risk Alerts</p>
              <p className="text-sm text-muted-foreground">Instant notification for high severity alerts</p>
            </div>
            <Switch defaultChecked />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-foreground">Medium-Risk Alerts</p>
              <p className="text-sm text-muted-foreground">Daily digest of medium severity alerts</p>
            </div>
            <Switch defaultChecked />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-foreground">Email Notifications</p>
              <p className="text-sm text-muted-foreground">Send alerts to registered email</p>
            </div>
            <Switch defaultChecked />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-foreground">Weekly Summary</p>
              <p className="text-sm text-muted-foreground">Receive weekly analytics summary</p>
            </div>
            <Switch />
          </div>
        </CardContent>
      </Card>

      {/* API Keys */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-primary">API Keys</CardTitle>
          <CardDescription>Manage API access for integrations</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-4 bg-secondary/30 rounded-lg border border-border">
            <p className="text-xs text-muted-foreground mb-2">Current API Key</p>
            <p className="font-mono text-sm text-foreground truncate">sk_live_1a2b3c4d5e6f7g8h9i0j...</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" className="border-border bg-transparent">
              Copy Key
            </Button>
            <Button variant="outline" className="border-border text-accent bg-transparent">
              Regenerate
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* System Preferences */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-primary">System Preferences</CardTitle>
          <CardDescription>Configure system-wide settings</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium text-foreground mb-2 block">Default Time Range</label>
            <Select defaultValue="7days">
              <SelectTrigger className="bg-input border-border">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="24hours">Last 24 Hours</SelectItem>
                <SelectItem value="7days">Last 7 Days</SelectItem>
                <SelectItem value="30days">Last 30 Days</SelectItem>
                <SelectItem value="custom">Custom Range</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="text-sm font-medium text-foreground mb-2 block">Records Per Page</label>
            <Select defaultValue="25">
              <SelectTrigger className="bg-input border-border">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="10">10</SelectItem>
                <SelectItem value="25">25</SelectItem>
                <SelectItem value="50">50</SelectItem>
                <SelectItem value="100">100</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Button className="bg-primary hover:bg-primary/90 text-primary-foreground">Save Preferences</Button>
        </CardContent>
      </Card>

      {/* Danger Zone */}
      <Card className="bg-card border-red-200 border-2">
        <CardHeader>
          <CardTitle className="text-red-600">Danger Zone</CardTitle>
          <CardDescription>Irreversible actions</CardDescription>
        </CardHeader>
        <CardContent>
          <Button variant="outline" className="border-red-600 text-red-600 hover:bg-red-50 bg-transparent">
            Reset All Settings to Default
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
