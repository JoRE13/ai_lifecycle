import SwiftUI

struct QueryResponseCard: View {
    let response: QueryResponse

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Label("Verdict: \(response.verdict)", systemImage: "checkmark.seal")
                Spacer()
                Text(response.response_type)
                    .font(.caption)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.blue.opacity(0.12))
                    .clipShape(Capsule())
            }
            .font(.subheadline)

            Text(response.message_is)
                .font(.body)
                .textSelection(.enabled)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
        .padding(14)
        .background(Color(.systemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .stroke(Color.gray.opacity(0.2), lineWidth: 1)
        )
    }
}
