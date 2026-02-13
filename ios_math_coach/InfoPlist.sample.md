Add these keys to your app `Info.plist` for local, non-HTTPS backend development:

```xml
<key>BACKEND_BASE_URL</key>
<string>http://YOUR_LAN_IP:8000</string>
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>
```

For production, use HTTPS and remove `NSAllowsArbitraryLoads`.
