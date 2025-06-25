#!/usr/bin/env python3
"""Create sample data for Query Hub"""
import asyncio
import sys
sys.path.append('.')

from app.core.database import AsyncSessionLocal
from app.models import Workspace, Query, WorkspacePermission
from app.models.workspace import WorkspaceType
from app.models.query import QueryStatus
from app.models.permission import PrincipalType


async def create_sample_data():
    async with AsyncSessionLocal() as db:
        try:
            # Create sample workspaces
            personal_ws = Workspace(
                name="My Personal Workspace",
                type=WorkspaceType.PERSONAL,
                owner_id="admin@example.com",  # 실제 사용자 ID로 변경 필요
                auto_close_days=90
            )
            
            team_ws = Workspace(
                name="Data Analytics Team",
                type=WorkspaceType.GROUP,
                owner_id="admin@example.com",
                auto_close_days=30
            )
            
            db.add(personal_ws)
            db.add(team_ws)
            await db.commit()
            
            # Create sample queries
            query1 = Query(
                workspace_id=personal_ws.id,
                name="Sales Report - Monthly",
                description="월별 매출 현황 조회",
                sql_template="""
                    SELECT 
                        DATE_FORMAT(order_date, '%Y-%m') as month,
                        COUNT(*) as order_count,
                        SUM(total_amount) as total_sales
                    FROM orders
                    WHERE order_date BETWEEN :start_date AND :end_date
                    GROUP BY month
                    ORDER BY month DESC
                """,
                params_info={
                    "start_date": {
                        "type": "date",
                        "label": "시작일",
                        "required": True
                    },
                    "end_date": {
                        "type": "date", 
                        "label": "종료일",
                        "required": True
                    }
                },
                status=QueryStatus.AVAILABLE,
                created_by="admin@example.com"
            )
            
            query2 = Query(
                workspace_id=team_ws.id,
                name="User Activity Dashboard",
                description="사용자 활동 통계",
                sql_template="""
                    SELECT 
                        u.name,
                        u.department,
                        COUNT(a.id) as activity_count,
                        MAX(a.created_at) as last_activity
                    FROM users u
                    LEFT JOIN activities a ON u.id = a.user_id
                    WHERE u.department = :department
                    GROUP BY u.id, u.name, u.department
                    ORDER BY activity_count DESC
                    LIMIT 20
                """,
                params_info={
                    "department": {
                        "type": "string",
                        "label": "부서명",
                        "required": True,
                        "default": "Engineering"
                    }
                },
                status=QueryStatus.UNAVAILABLE,
                created_by="admin@example.com"
            )
            
            query3 = Query(
                workspace_id=personal_ws.id,
                name="Product Inventory Status",
                description="재고 현황 조회 (파라미터 없음)",
                sql_template="""
                    SELECT 
                        p.product_name,
                        p.category,
                        i.quantity,
                        i.last_updated
                    FROM products p
                    JOIN inventory i ON p.id = i.product_id
                    WHERE i.quantity < 100
                    ORDER BY i.quantity ASC
                """,
                params_info=None,
                status=QueryStatus.AVAILABLE,
                created_by="admin@example.com"
            )
            
            db.add(query1)
            db.add(query2)
            db.add(query3)
            await db.commit()
            
            # Create sample permissions
            perm1 = WorkspacePermission(
                workspace_id=team_ws.id,
                principal_type=PrincipalType.USER,
                principal_id="user1@example.com"
            )
            
            perm2 = WorkspacePermission(
                workspace_id=team_ws.id,
                principal_type=PrincipalType.GROUP,
                principal_id="data-team"
            )
            
            db.add(perm1)
            db.add(perm2)
            await db.commit()
            
            print("✅ Sample data created successfully!")
            print(f"  - Created 2 workspaces")
            print(f"  - Created 3 queries") 
            print(f"  - Created 2 permissions")
            
        except Exception as e:
            print(f"❌ Error creating sample data: {e}")
            await db.rollback()


if __name__ == "__main__":
    asyncio.run(create_sample_data())