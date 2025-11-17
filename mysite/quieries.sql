SELECT
    "auth_user"."id",
    "auth_user"."password",
    "auth_user"."last_login",
    "auth_user"."is_superuser",
    "auth_user"."username",
    "auth_user"."first_name",
    "auth_user"."last_name",
    "auth_user"."email",
    "auth_user"."is_staff",
    "auth_user"."is_active",
    "auth_user"."date_joined"
FROM "auth_user"
WHERE "auth_user"."username" = 'admin_Vladimir' LIMIT 21;
UPDATE "auth_user" SET "last_login" = '2025-11-08 16:38:08.825283' WHERE "auth_user"."id" = 2;

SELECT
    "shopapp_product"."shopapp_product"."id",
    "shopapp_product"."name",
    "shopapp_product"."description",
    "shopapp_product"."price",
    "shopapp_product"."discount",
    "shopapp_product"."created_at",
    "shopapp_product"."archived",
    "shopapp_product"."preview",
    "shopapp_product"."created_by_id"
FROM "shopapp_product"
WHERE "shopapp_product"."id" = 1 LIMIT 21;

SELECT
    "shopapp_productimage"."id",
    "shopapp_productimage"."product_id",
    "shopapp_productimage"."image",
    "shopapp_productimage"."description"
FROM "shopapp_productimage"
WHERE "shopapp_productimage"."product_id" IN (1);
