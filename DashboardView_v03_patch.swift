import SwiftUI

struct TMStatus: Codable {
    var destination: String?
    var latest_backup_iso: String?
    var hours_since_latest: Double?
    var stale: Bool
    var generated_at: String
    var ok: Bool
}

struct ResticStatus: Codable {
    var repository: String?
    var latest_snapshot_iso: String?
    var hours_since_latest: Double?
    var snapshot_id: String?
    var hostname: String?
    var stale: Bool
    var generated_at: String
    var ok: Bool
    var error: String?
}

struct DashboardView: View {
    @State private var tmStatus: TMStatus? = nil
    @State private var resticStatus: ResticStatus? = nil
    @State private var tmStatusText: String = "—"
    @State private var tmDestinationText: String = "—"
    @State private var offsiteStatusText: String = "—"
    @State private var offsiteRepositoryText: String = "—"

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("MacAgent Backup").font(.largeTitle).bold()

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
                Card(title: "Off-site", subtitle: offsiteRepositoryText, actionTitle: "Refresh") {
                    refreshOffsiteStatus()
                }
            }

            HStack(spacing: 12) {
                Card(title: "Off-site Status", subtitle: offsiteStatusText, actionTitle: "Backup Now") {
                    _ = runWorker(["offsite-run"]) // off-site job
                    refreshOffsiteStatus()
                }
                Card(title: "Rapid Recovery", subtitle: "Prepare external", actionTitle: "Prepare") {
                    _ = runWorker(["install-external","/Volumes/MacAgent-Rescue"]) // installer handoff
                }
                Card(title: "Integrity", subtitle: "Restore drill", actionTitle: "Run Drill") {
                    _ = runWorker(["restore-drill"]) // test restore
                }
                Card(title: "Integrity", subtitle: "Weekly verify", actionTitle: "Verify Now") {
                    _ = runWorker(["verify-weekly"]) // checksum test
                }
            }

            Spacer()
        }
        .padding(20)
        .onAppear { 
            refreshTMStatus()
            refreshOffsiteStatus()
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
            let (_, out) = runWorkerCapture(["offsite-status"]) // stdout is JSON
            guard let data = out.data(using: .utf8), !out.isEmpty else {
                DispatchQueue.main.async {
                    self.offsiteStatusText = "Unavailable"
                    self.offsiteRepositoryText = "(no repository)"
                }
                return
            }
            do {
                let decoded = try JSONDecoder().decode(ResticStatus.self, from: data)
                DispatchQueue.main.async {
                    self.resticStatus = decoded
                    
                    // Format repository display
                    if let repo = decoded.repository {
                        if repo.hasPrefix("s3:") {
                            self.offsiteRepositoryText = "S3: \(repo.components(separatedBy: "/").last ?? repo)"
                        } else if repo.hasPrefix("/") {
                            self.offsiteRepositoryText = "Local: \(repo.components(separatedBy: "/").last ?? repo)"
                        } else {
                            self.offsiteRepositoryText = repo
                        }
                    } else {
                        self.offsiteRepositoryText = "(no repository)"
                    }
                    
                    // Format status text
                    if let error = decoded.error {
                        self.offsiteStatusText = "Error: \(error)"
                    } else if let hrs = decoded.hours_since_latest {
                        if hrs < 1 { self.offsiteStatusText = "Just backed up" }
                        else if hrs < 24 { self.offsiteStatusText = String(format: "%.1f h ago", hrs) }
                        else if hrs < 48 { self.offsiteStatusText = String(format: "%.1f h ago", hrs) }
                        else { self.offsiteStatusText = String(format: "%.1f h ago — %@", hrs, decoded.ok ? "OK" : "STALE") }
                    } else {
                        self.offsiteStatusText = "No snapshots yet"
                    }
                }
            } catch {
                DispatchQueue.main.async {
                    self.offsiteStatusText = "Parse error"
                    self.offsiteRepositoryText = "(error)"
                }
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