from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from app.application.services.invitation_code_service import InvitationCodeService
from app.domain.exceptions.conflict_with_existing_resource_exception import (
    ConflictWithExistingResourceException,
)
from app.domain.exceptions.resource_not_found_exception import ResourceNotFoundException
from app.infrastructure.dto.invitation_code_dto import InvitationCodeDTO
from app.infrastructure.dto.invitation_code_request_dto import InvitationCodeRequestDTO
from app.infrastructure.dto.authenticated_user_dto import AuthenticatedUserDTO
from app.infrastructure.mappers.invitation_code_mappers import (
    map_invitation_code_model_to_invitation_code_dto,
)
from app.infrastructure.middlewares.protect_route_middleware import (
    protect_route_middlware,
)
from app.infrastructure.repositories.relational_database_invitation_code_repository_impl import (
    RelationalDatabaseInvitationCodeRepositoryImpl,
)
from app.infrastructure.repositories.relational_database_user_repository_impl import (
    RelationalDatabaseUserRepositoryImpl,
)

invitation_code_router = APIRouter()
invitation_code_service = InvitationCodeService(
    invitation_code_repository=RelationalDatabaseInvitationCodeRepositoryImpl(),
    user_repository=RelationalDatabaseUserRepositoryImpl(),
)


@invitation_code_router.get("", status_code=status.HTTP_200_OK)
def get_all_invitation_codes(
    authenticated_user: Annotated[
        AuthenticatedUserDTO, Depends(protect_route_middlware)
    ],
) -> list[InvitationCodeDTO]:
    logger.info("API REQUEST - GET /invitation-code/")
    invitation_codes = invitation_code_service.get_all_invitation_codes_by_user_id(
        authenticated_user.id
    )
    logger.success(f"API RESPONSE {status.HTTP_200_OK} - GET /invitation-code/")
    return [
        map_invitation_code_model_to_invitation_code_dto(invitation_code)
        for invitation_code in invitation_codes
    ]


@invitation_code_router.post("", status_code=status.HTTP_201_CREATED)
def create_invitation_code(
    invitation_code_request_dto: InvitationCodeRequestDTO,
    authenticated_user: Annotated[
        AuthenticatedUserDTO, Depends(protect_route_middlware)
    ],
) -> InvitationCodeDTO:
    try:
        logger.info("API REQUEST - POST /invitation-code/")
        logger.debug(f"Request body: {invitation_code_request_dto.model_dump()}")
        invitation_code = invitation_code_service.create_invitation_code(
            recipient_email=invitation_code_request_dto.email,
            authenticated_user_id=authenticated_user.id,
        )
        logger.success(f"API RESPONSE {status.HTTP_201_CREATED} - POST /invitation-code/")
        return map_invitation_code_model_to_invitation_code_dto(invitation_code)
    except ConflictWithExistingResourceException:
        error_detail = "An invitation code has already been generated for the email above"
        logger.warning(f"API RESPONSE {status.HTTP_409_CONFLICT} - POST /invitation-code/ - {error_detail}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_detail,
        )


@invitation_code_router.patch("/{invitation_code}", status_code=status.HTTP_200_OK)
def change_recipient_email_from_invitation_code(
    invitation_code: str,
    invitation_code_request_dto: InvitationCodeRequestDTO,
    authenticated_user: Annotated[
        AuthenticatedUserDTO, Depends(protect_route_middlware)
    ],
) -> InvitationCodeDTO:
    try:
        logger.info(f"API REQUEST - PATCH /invitation-code/{invitation_code}")
        logger.debug(f"Request body: {invitation_code_request_dto.model_dump()}")
        updated_invitation_code = invitation_code_service.update_recipient_email_from_invitation_code(
            code=invitation_code,
            recipient_email=invitation_code_request_dto.email,
            authenticated_user_id=authenticated_user.id,
        )
        logger.success(f"API RESPONSE {status.HTTP_200_OK} - PATCH /invitation-code/{invitation_code}")
        return map_invitation_code_model_to_invitation_code_dto(updated_invitation_code)
    except ResourceNotFoundException:
        error_detail = "Invitation code not found"
        logger.warning(f"API RESPONSE {status.HTTP_404_NOT_FOUND} - PATCH /invitation-code/{invitation_code} - {error_detail}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_detail,
        )
    except ConflictWithExistingResourceException:
        error_detail = "An invitation code has already been generated for the email above"
        logger.warning(f"API RESPONSE {status.HTTP_409_CONFLICT} - PATCH /invitation-code/{invitation_code} - {error_detail}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_detail,
        )


@invitation_code_router.delete(
    "/{invitation_code}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_invitation_code(
    invitation_code: str,
    authenticated_user: Annotated[
        AuthenticatedUserDTO, Depends(protect_route_middlware)
    ],
) -> None:
    try:
        logger.info(f"API REQUEST - DELETE /invitation-code/{invitation_code}")
        invitation_code_service.delete_invitation_code_by_code(
            code=invitation_code, authenticated_user_id=authenticated_user.id
        )
        logger.success(f"API RESPONSE {status.HTTP_204_NO_CONTENT} - DELETE /invitation-code/{invitation_code}")
    except ResourceNotFoundException:
        error_detail = "Invitation code not found"
        logger.warning(f"API RESPONSE {status.HTTP_404_NOT_FOUND} - DELETE /invitation-code/{invitation_code} - {error_detail}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_detail,
        )
