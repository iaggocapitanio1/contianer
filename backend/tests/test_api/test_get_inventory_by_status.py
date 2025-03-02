import pytest
from fastapi import status
from tests.conftest import AsyncClientCustom
from tests.fixture import UserFactory


@pytest.mark.anyio
@pytest.mark.parametrize(
    "status, order_type, skip, limit, expected_status",
    [
        ("All", "All", 0, 10, status.HTTP_200_OK),  # ✅ General case
        ("Available", "PURCHASE", 0, 5, status.HTTP_200_OK),  # ✅ Specific category
        ("Attached", "RENT", 5, 10, status.HTTP_200_OK),  # ✅ Pagination test
        ("Delivered", "RENT_TO_OWN", 10, 20, status.HTTP_200_OK),  # ✅ Large page size
        ("InvalidStatus", "INVALID", 0, 10, status.HTTP_400_BAD_REQUEST),  # ❌ Invalid input should return 400
    ],
)
async def test_get_inventory_by_status(client: AsyncClientCustom, status, order_type, skip, limit, expected_status):
    """
    Test the /inventory_by_status endpoint with different parameters and authentication.
    """

    # ✅ Attempt unauthorized request (should fail)
    response = await client.get(
        "/inventory_by_status",
        params={"status": status, "order_type": order_type, "skip": skip, "limit": limit},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # ✅ Authenticate using force_login (NO USER CREATION)
    user = await UserFactory.create()
    client.force_login(user)

    # ✅ Send authorized request
    response = await client.get(
        "/inventory_by_status",
        params={"status": status, "order_type": order_type, "skip": skip, "limit": limit},
    )

    # ✅ Validate response status
    assert response.status_code == expected_status, f"Unexpected status code: {response.status_code}"

    # ✅ Validate response structure for successful cases
    if expected_status == status.HTTP_200_OK:
        data = response.json()

        assert isinstance(data, dict), "Response should be a dictionary"
        assert "count" in data, "Missing 'count' in response"
        assert isinstance(data["count"], int), "'count' should be an integer"
        assert "results" in data, "Missing 'results' in response"
        assert isinstance(data["results"], list), "'results' should be a list"
        assert "next" in data, "Missing 'next' pagination field"
        assert "previous" in data, "Missing 'previous' pagination field"
