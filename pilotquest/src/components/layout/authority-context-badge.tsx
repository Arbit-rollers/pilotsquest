import { Badge } from "@/components/ui/badge";
import { formatAuthorityContext, type AuthorityContext } from "@/lib/types/authority-context";

/**
 * Reduces accidental jurisdiction confusion (PRD §215). Rendered on
 * dashboard, study session, and progress screens.
 */
export function AuthorityContextBadge({ context }: { context: AuthorityContext }) {
  return (
    <Badge variant="outline" className="font-normal text-xs">
      {formatAuthorityContext(context)}
    </Badge>
  );
}
