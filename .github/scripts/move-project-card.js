// Moves an issue's card on the "Music Repertoire" user Project (v2) to a given Status column.
// Project/field/option IDs are hardcoded below — they're stable for a given project, but if the
// project is ever deleted and recreated, regenerate them with:
//   gh project field-list <number> --owner AleFire99 --format json
const PROJECT_ID = "PVT_kwHOBZshzM4BgB13";
const STATUS_FIELD_ID = "PVTSSF_lAHOBZshzM4BgB13zhaQcl4";

function extractIssueNumbers(branch, body) {
  const numbers = new Set();
  const branchMatch = (branch || "").match(/issue-(\d+)/);
  if (branchMatch) numbers.add(Number(branchMatch[1]));

  const closingKeywords = /\b(close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved)\s+#(\d+)/gi;
  let match;
  while ((match = closingKeywords.exec(body || "")) !== null) {
    numbers.add(Number(match[2]));
  }
  return [...numbers];
}

module.exports = async ({ github, context, core }) => {
  const branch = process.env.BRANCH || "";
  const body = process.env.BODY || "";
  const statusOptionId = process.env.STATUS_OPTION_ID;

  const issueNumbers = extractIssueNumbers(branch, body);
  if (issueNumbers.length === 0) {
    core.info(`No issue reference found in branch "${branch}" or PR body — nothing to move.`);
    return;
  }

  for (const number of issueNumbers) {
    try {
      const issueQuery = await github.graphql(
        `query($owner: String!, $repo: String!, $number: Int!) {
          repository(owner: $owner, name: $repo) {
            issue(number: $number) { id }
          }
        }`,
        { owner: context.repo.owner, repo: context.repo.repo, number }
      );
      const contentId = issueQuery.repository.issue?.id;
      if (!contentId) {
        core.warning(`Issue #${number} not found — skipping.`);
        continue;
      }

      const addResult = await github.graphql(
        `mutation($projectId: ID!, $contentId: ID!) {
          addProjectV2ItemById(input: { projectId: $projectId, contentId: $contentId }) {
            item { id }
          }
        }`,
        { projectId: PROJECT_ID, contentId }
      );
      const itemId = addResult.addProjectV2ItemById.item.id;

      await github.graphql(
        `mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
          updateProjectV2ItemFieldValue(input: {
            projectId: $projectId
            itemId: $itemId
            fieldId: $fieldId
            value: { singleSelectOptionId: $optionId }
          }) { projectV2Item { id } }
        }`,
        { projectId: PROJECT_ID, itemId, fieldId: STATUS_FIELD_ID, optionId: statusOptionId }
      );

      core.info(`Moved issue #${number} to status option ${statusOptionId}.`);
    } catch (error) {
      core.warning(`Failed to move issue #${number}: ${error.message}`);
    }
  }
};
