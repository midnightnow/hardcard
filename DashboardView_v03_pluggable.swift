import SwiftUI

struct TMStatus: Codable {
    var destination: String?
    var latest_backup_iso: String?
    var hours_since_latest: Double?
    var stale: Bool
    var generated_at: String
    var ok: Bool
}

struct OffsiteStatus: Codable {
    var provider: String?
    var repository: String?
    var latest_backup_iso: String?
    var hours_since_latest: Double?
    var backup_id: String?
    var hostname: String?
    var stale: Bool
    var generated_at: String
    var ok: Bool
    var error: String?
    var size_bytes: Int?
    var file_count: Int?
}

struct BackupProvider: Codable {
    var provider: String
    var available: Bool
    var configured: Bool
    var last_backup: String?
    var repository: String?
    var status_summary: String
}

struct ProvidersResponse: Codable {
    var providers: [BackupProvider]
    var primary_provider: String?
    var total_available: Int
    var generated_at: String
}

struct DashboardView: View {
    @State private var tmStatus: TMStatus? = nil
    @State private var offsiteStatus: OffsiteStatus? = nil
    @State private var providers: [BackupProvider] = []
    @State private var tmStatusText: String = "—"
    @State private var tmDestinationText: String = "—"
    @State private var offsiteStatusText: String = "—"
    @State private var offsiteProviderText: String = "—"
    @State private var showProviderSelector: Bool = false

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("MacAgent Backup").font(.largeTitle).bold()
            
            // 3-2-1 Strategy Status Bar
            HStack {
                Circle()
                    .fill(tmStatus?.ok == true ? Color.green : Color.orange)
                    .frame(width: 12, height: 12)
                Text("Local")
                
                Spacer()
                
                Circle()
                    .fill(offsiteStatus?.ok == true ? Color.green : Color.orange)
                    .frame(width: 12, height: 12)
                Text("Off-site")
                
                Spacer()
                
                Text("3-2-1 Strategy: \((tmStatus?.ok == true && offsiteStatus?.ok == true) ? "✅ Compliant" : "⚠️ Needs Attention")")
                    .font(.caption)
                    .foregroundColor((tmStatus?.ok == true && offsiteStatus?.ok == true) ? .green : .orange)
            }
            .padding(.horizontal)
            .padding(.vertical, 8)
            .background(Color(NSColor.controlBackgroundColor))
            .cornerRadius(8)

            HStack(spacing: 12) {
                Card(title: "Time Machine", subtitle: "Status", actionTitle: "Run Now") {
                    _ = runWorker(["tm-check"]) // fire-and-forget health check
                    refreshTMStatus()
                }
                Card(title: "Time Machine", subtitle: tmDestinationText, actionTitle: "Refresh") {
                    refreshTMStatus()
                }
                Card(title: "Last Backup", subtitle: tmStatusText, actionTitle: "Refresh") {
                    refreshTMStatus()
                }
                Card(title: "Off-site Provider", subtitle: offsiteProviderText, actionTitle: "Switch") {
                    showProviderSelector.toggle()
                }
            }

            HStack(spacing: 12) {
                Card(title: "Off-site Status", subtitle: offsiteStatusText, actionTitle: "Backup Now") {
                    _ = runWorker(["offsite-run"]) // off-site job
                    refreshOffsiteStatus()
                }
                Card(title: "Providers", subtitle: "\(providers.filter { $0.available }.count) available", actionTitle: "Check All") {
                    _ = runWorker(["offsite-check"])
                    refreshProviders()
                }
                Card(title: "Integrity", subtitle: "Restore drill", actionTitle: "Run Drill") {
                    _ = runWorker(["restore-drill"]) // test restore
                }
                Card(title: "Summary", subtitle: "Full status", actionTitle: "View All") {
                    _ = runWorker(["backup-summary"])
                }
            }

            Spacer()
        }
        .padding(20)
        .sheet(isPresented: $showProviderSelector) {
            ProviderSelectorView(providers: providers, onProviderSelected: { provider in
                // This would switch to a specific provider if implemented
                showProviderSelector = false
                refreshOffsiteStatus()
            })
        }
        .onAppear { 
            refreshTMStatus()
            refreshOffsiteStatus()
            refreshProviders()
        }
    }

    private func refreshTMStatus() {
        DispatchQueue.global(qos: .userInitiated).async {
            let (_, out) = runWorkerCapture(["tm-status"]) // stdout is JSON
            guard let data = out.data(using: .utf8), !out.isEmpty else {
                DispatchQueue.main.async {
                    self.tmStatusText = "Unavailable"
                    self.tmDestinationText = "(no destination)"
                }
                return
            }
            do {
                let decoded = try JSONDecoder().decode(TMStatus.self, from: data)
                DispatchQueue.main.async {
                    self.tmStatus = decoded
                    self.tmDestinationText = decoded.destination ?? "(no destination)"
                    if let hrs = decoded.hours_since_latest {
                        if hrs < 0.5 { self.tmStatusText = "Just now" }
                        else if hrs < 24 { self.tmStatusText = String(format: "%.1f h ago", hrs) }
                        else { self.tmStatusText = String(format: "%.1f h ago — %@", hrs, decoded.ok ? "OK" : "STALE") }
                    } else {
                        self.tmStatusText = "No backups yet"
                    }
                }
            } catch {
                DispatchQueue.main.async {
                    self.tmStatusText = "Parse error"
                    self.tmDestinationText = "(error)"
                }
            }
        }
    }
    
    private func refreshOffsiteStatus() {
        DispatchQueue.global(qos: .userInitiated).async {
            let (_, out) = runWorkerCapture(["offsite-status"]) // stdout is JSON with auto-detection
            guard let data = out.data(using: .utf8), !out.isEmpty else {
                DispatchQueue.main.async {
                    self.offsiteStatusText = "Unavailable"
                    self.offsiteProviderText = "(no providers)"
                }
                return
            }
            do {
                let decoded = try JSONDecoder().decode(OffsiteStatus.self, from: data)
                DispatchQueue.main.async {
                    self.offsiteStatus = decoded
                    
                    // Format provider display
                    if let provider = decoded.provider {
                        self.offsiteProviderText = provider.capitalized
                        
                        // Add repository info if available
                        if let repo = decoded.repository {
                            if repo.hasPrefix("s3:") {
                                self.offsiteProviderText += " (S3)"
                            } else if repo.hasPrefix("b2:") {
                                self.offsiteProviderText += " (B2)"
                            } else if repo.hasPrefix("/") {
                                self.offsiteProviderText += " (Local)"
                            }
                        }
                    } else {
                        self.offsiteProviderText = "(no providers)"
                    }
                    
                    // Format status text
                    if let error = decoded.error {
                        if error.contains("not installed") {
                            self.offsiteStatusText = "Not installed"
                        } else if error.contains("not configured") {
                            self.offsiteStatusText = "Not configured"
                        } else {
                            self.offsiteStatusText = "Error"
                        }
                    } else if let hrs = decoded.hours_since_latest {
                        if hrs < 1 { self.offsiteStatusText = "Just backed up" }
                        else if hrs < 24 { self.offsiteStatusText = String(format: "%.1f h ago", hrs) }
                        else if hrs < 48 { self.offsiteStatusText = String(format: "%.1f h ago", hrs) }
                        else { self.offsiteStatusText = String(format: "%.1f h ago — %@", hrs, decoded.ok ? "OK" : "STALE") }
                    } else {
                        self.offsiteStatusText = "No backups yet"
                    }
                }
            } catch {
                DispatchQueue.main.async {
                    self.offsiteStatusText = "Parse error"
                    self.offsiteProviderText = "(error)"
                }
            }
        }
    }
    
    private func refreshProviders() {
        DispatchQueue.global(qos: .userInitiated).async {
            let (_, out) = runWorkerCapture(["offsite-providers"])
            guard let data = out.data(using: .utf8), !out.isEmpty else {
                return
            }
            do {
                let decoded = try JSONDecoder().decode(ProvidersResponse.self, from: data)
                DispatchQueue.main.async {
                    self.providers = decoded.providers
                }
            } catch {
                // Silently fail for provider refresh
            }
        }
    }
}

struct Card: View {
    let title: String
    let subtitle: String
    let actionTitle: String
    let action: () -> Void
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title).font(.headline)
            Text(subtitle).font(.subheadline)
            Button(actionTitle, action: action)
        }
        .padding()
        .background(Color(NSColor.windowBackgroundColor))
        .cornerRadius(12)
        .shadow(radius: 1)
    }
}

struct ProviderSelectorView: View {
    let providers: [BackupProvider]
    let onProviderSelected: (BackupProvider) -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Backup Providers").font(.title2).bold()
            
            ForEach(providers, id: \.provider) { provider in
                HStack {
                    VStack(alignment: .leading) {
                        Text(provider.provider.capitalized)
                            .font(.headline)
                        Text(provider.status_summary)
                            .font(.caption)
                            .foregroundColor(.secondary)
                        if let repo = provider.repository {
                            Text(repo)
                                .font(.caption2)
                                .foregroundColor(.secondary)
                        }
                    }
                    
                    Spacer()
                    
                    if provider.available {
                        if provider.configured {
                            Button("Select") {
                                onProviderSelected(provider)
                            }
                            .buttonStyle(.borderedProminent)
                        } else {
                            Button("Configure") {
                                // Would open configuration UI
                            }
                            .buttonStyle(.bordered)
                        }
                    } else {
                        Text("Not Available")
                            .foregroundColor(.secondary)
                    }
                }
                .padding()
                .background(Color(NSColor.controlBackgroundColor))
                .cornerRadius(8)
            }
            
            Spacer()
        }
        .padding()
        .frame(minWidth: 500, minHeight: 400)
    }
}