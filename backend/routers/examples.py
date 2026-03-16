from fastapi import APIRouter, HTTPException
from models.intake import BlastRadiusRequest, Service, Dependency, Team, Decision

router = APIRouter(prefix="/examples")

EXAMPLES = {
    "db-migration": BlastRadiusRequest(
        services=[
            Service(
                id="auth-service",
                name="Authentication Service",
                owner_team="platform",
                criticality="critical",
                description="Handles all user authentication, session creation, and token validation. Issues JWTs for all downstream services.",
            ),
            Service(
                id="user-profile-service",
                name="User Profile Service",
                owner_team="product",
                criticality="high",
                description="Stores and serves user profile data, preferences, and account metadata. Backed by the shared PostgreSQL database.",
            ),
            Service(
                id="session-manager",
                name="Session Manager",
                owner_team="platform",
                criticality="critical",
                description="Manages active user sessions, token refresh, and session invalidation. Directly queries auth database.",
            ),
            Service(
                id="api-gateway",
                name="API Gateway",
                owner_team="devex",
                criticality="high",
                description="Routes all external traffic. Calls auth-service for token validation on every request.",
            ),
            Service(
                id="notification-service",
                name="Notification Service",
                owner_team="devex",
                criticality="medium",
                description="Sends emails and push notifications. Reads user contact info from user-profile-service asynchronously.",
            ),
        ],
        dependencies=[
            Dependency(from_service="api-gateway", to_service="auth-service", dependency_type="sync-api", strength="hard"),
            Dependency(from_service="auth-service", to_service="user-profile-service", dependency_type="database", strength="hard"),
            Dependency(from_service="session-manager", to_service="auth-service", dependency_type="sync-api", strength="hard"),
            Dependency(from_service="notification-service", to_service="user-profile-service", dependency_type="async-event", strength="soft"),
        ],
        teams=[
            Team(id="platform", name="Platform Team", owns=["auth-service", "session-manager"], size=6, focus="platform"),
            Team(id="product", name="Product Team", owns=["user-profile-service"], size=8, focus="product"),
            Team(id="devex", name="Developer Experience Team", owns=["api-gateway", "notification-service"], size=5, focus="platform"),
        ],
        decision=Decision(
            title="Migrating user auth database from PostgreSQL to Aurora",
            description="Hard cutover migration of the authentication and user profile PostgreSQL database to AWS Aurora PostgreSQL. Planned as an immediate maintenance window cutover. Aurora provides better read replica performance and automatic failover, but the migration requires schema validation and connection string updates across all services that query the database directly.",
            decision_type="migration",
            affected_services=["auth-service", "user-profile-service"],
            timeline="immediate",
            reversibility="hard",
        ),
        additional_context="Migration is being driven by a cost optimization initiative. The team has not yet audited all services that connect directly to the PostgreSQL instance. Session-manager was found to have a direct database connection that was undocumented.",
    ),

    "api-deprecation": BlastRadiusRequest(
        services=[
            Service(id="payments-v1", name="Payments API v1", owner_team="payments", criticality="critical", description="Legacy payments API serving checkout flows and 3 external partner integrations. REST API with XML response format."),
            Service(id="payments-v2", name="Payments API v2", owner_team="payments", criticality="critical", description="New payments API with JSON responses, webhook support, and improved retry logic. Target migration destination."),
            Service(id="checkout-service", name="Checkout Service", owner_team="growth", criticality="critical", description="Core checkout flow. Currently calls payments-v1. Migration to v2 is in progress but not complete."),
            Service(id="billing-service", name="Billing Service", owner_team="payments", criticality="high", description="Handles subscription billing, invoicing, and payment method management. Uses payments-v1 for recurring charges."),
            Service(id="analytics-pipeline", name="Analytics Pipeline", owner_team="data", criticality="medium", description="Ingests payment events from v1 API for revenue reporting. Has custom parsing logic for v1 response format."),
            Service(id="mobile-app-backend", name="Mobile App Backend", owner_team="growth", criticality="high", description="Backend for iOS and Android apps. Calls payments-v1 for in-app purchases. Mobile release cycle is 2 weeks."),
            Service(id="partner-integration-layer", name="Partner Integration Layer", owner_team="partner-eng", criticality="high", description="Manages 3 external partner integrations (Acme Corp, Beta Inc, Gamma Ltd) all consuming payments-v1 via XML API."),
        ],
        dependencies=[
            Dependency(from_service="checkout-service", to_service="payments-v1", dependency_type="sync-api", strength="hard"),
            Dependency(from_service="checkout-service", to_service="payments-v2", dependency_type="sync-api", strength="soft"),
            Dependency(from_service="billing-service", to_service="payments-v1", dependency_type="sync-api", strength="hard"),
            Dependency(from_service="analytics-pipeline", to_service="payments-v1", dependency_type="async-event", strength="soft"),
            Dependency(from_service="mobile-app-backend", to_service="payments-v1", dependency_type="sync-api", strength="hard"),
            Dependency(from_service="partner-integration-layer", to_service="payments-v1", dependency_type="sync-api", strength="hard"),
        ],
        teams=[
            Team(id="payments", name="Payments Team", owns=["payments-v1", "payments-v2", "billing-service"], size=7, focus="product"),
            Team(id="growth", name="Growth Team", owns=["checkout-service", "mobile-app-backend"], size=9, focus="product"),
            Team(id="data", name="Data Team", owns=["analytics-pipeline"], size=5, focus="data"),
            Team(id="partner-eng", name="Partner Engineering", owns=["partner-integration-layer"], size=4, focus="product"),
        ],
        decision=Decision(
            title="Deprecating v1 Payments API — 90-day sunset",
            description="Sunset the v1 Payments API (XML-based REST) in 90 days. All internal consumers must migrate to v2. External partners will receive 60-day notice via API deprecation header before hard shutdown. v2 is a breaking change: JSON only, different endpoint structure, new auth mechanism.",
            decision_type="api-change",
            affected_services=["payments-v1"],
            timeline="months",
            reversibility="moderate",
        ),
        additional_context="The 90-day timeline is driven by a PCI compliance audit requirement to reduce attack surface. The partner-integration-layer team has confirmed that one partner (Gamma Ltd) has indicated they cannot migrate in under 6 months due to their own release cycle.",
    ),

    "platform-reorg": BlastRadiusRequest(
        services=[
            Service(id="ci-cd-platform", name="CI/CD Platform", owner_team="platform", criticality="critical", description="Internal CI/CD tooling, pipeline infrastructure, and developer tooling. Transitioning to DevEx team."),
            Service(id="k8s-cluster-mgmt", name="Kubernetes Cluster Management", owner_team="platform", criticality="critical", description="Cluster provisioning, scaling, and node management. Transitioning to Infra team."),
            Service(id="secrets-management", name="Secrets Management Service", owner_team="platform", criticality="critical", description="Vault integration, secret rotation, and access control. Ownership TBD between Infra and Security."),
            Service(id="service-mesh", name="Service Mesh (Istio)", owner_team="platform", criticality="high", description="mTLS, traffic management, and observability. Transitioning to Infra team."),
            Service(id="internal-dev-portal", name="Internal Developer Portal", owner_team="platform", criticality="medium", description="Internal tooling docs and service catalog. Transitioning to DevEx team."),
            Service(id="monitoring-stack", name="Monitoring & Alerting Stack", owner_team="platform", criticality="high", description="Prometheus, Grafana, alerting rules. Joint ownership during transition."),
            Service(id="auth-service", name="Authentication Service", owner_team="product", criticality="critical", description="Depends on secrets-management and service-mesh. Ownership unchanged but affected by platform reorg."),
            Service(id="payments-core", name="Payments Core", owner_team="product", criticality="critical", description="Depends on k8s-cluster-mgmt for deployment and secrets-management for credentials."),
        ],
        dependencies=[
            Dependency(from_service="auth-service", to_service="secrets-management", dependency_type="sync-api", strength="hard"),
            Dependency(from_service="auth-service", to_service="service-mesh", dependency_type="shared-library", strength="hard"),
            Dependency(from_service="payments-core", to_service="k8s-cluster-mgmt", dependency_type="sync-api", strength="hard"),
            Dependency(from_service="payments-core", to_service="secrets-management", dependency_type="sync-api", strength="hard"),
            Dependency(from_service="ci-cd-platform", to_service="k8s-cluster-mgmt", dependency_type="sync-api", strength="hard"),
            Dependency(from_service="monitoring-stack", to_service="k8s-cluster-mgmt", dependency_type="sync-api", strength="soft"),
        ],
        teams=[
            Team(id="platform", name="Platform Team (splitting)", owns=["ci-cd-platform", "k8s-cluster-mgmt", "secrets-management", "service-mesh", "internal-dev-portal", "monitoring-stack"], size=10, focus="platform"),
            Team(id="product", name="Product Engineering", owns=["auth-service", "payments-core"], size=20, focus="product"),
            Team(id="security", name="Security Team", owns=[], size=4, focus="security"),
            Team(id="data", name="Data Team", owns=[], size=6, focus="data"),
        ],
        decision=Decision(
            title="Splitting Platform team into Infrastructure and Developer Experience sub-teams",
            description="The 10-person Platform team will be split into two sub-teams: Infrastructure (5 engineers, owns k8s, service-mesh, monitoring) and Developer Experience (5 engineers, owns CI/CD, dev portal, internal tooling). Secrets management ownership is contested — candidates are Infra team or Security team. Split is effective in 3 weeks. No service code changes. All changes are ownership, on-call rotation, and escalation path.",
            decision_type="reorg",
            affected_services=["ci-cd-platform", "k8s-cluster-mgmt", "secrets-management", "service-mesh", "internal-dev-portal", "monitoring-stack"],
            timeline="weeks",
            reversibility="moderate",
        ),
        additional_context="This reorg was triggered by the VP Engineering after Platform team's on-call burden became unsustainable. Two senior engineers have expressed intent to leave if the reorg is not handled carefully. The secrets-management ownership gap is the highest-risk unresolved item — it currently has no owner assigned post-split.",
    ),
}

EXAMPLE_METADATA = [
    {"id": "db-migration", "title": "Database Migration", "description": "Migrating user auth database from PostgreSQL to Aurora"},
    {"id": "api-deprecation", "title": "API Deprecation", "description": "Deprecating v1 Payments API — 90-day sunset"},
    {"id": "platform-reorg", "title": "Platform Team Reorg", "description": "Splitting Platform team into Infrastructure and Developer Experience sub-teams"},
]


@router.get("")
async def list_examples():
    return EXAMPLE_METADATA


@router.get("/{example_id}")
async def get_example(example_id: str):
    if example_id not in EXAMPLES:
        raise HTTPException(status_code=404, detail=f"Example '{example_id}' not found")
    return EXAMPLES[example_id]
