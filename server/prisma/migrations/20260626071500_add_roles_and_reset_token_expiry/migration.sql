-- CreateEnum
CREATE TYPE "Role" AS ENUM ('USER', 'ADMIN');

-- AlterTable
ALTER TABLE "users"
ADD COLUMN "role" "Role" NOT NULL DEFAULT 'USER',
ADD COLUMN "password_reset_token_hash" VARCHAR(255),
ADD COLUMN "password_reset_expires_at" TIMESTAMP(3);

-- CreateIndex
CREATE INDEX "users_role_idx" ON "users"("role");

-- CreateIndex
CREATE INDEX "users_password_reset_token_hash_idx" ON "users"("password_reset_token_hash");

-- CreateIndex
CREATE INDEX "refresh_tokens_user_id_session_id_isActive_expires_at_idx" ON "refresh_tokens"("user_id", "session_id", "isActive", "expires_at");
