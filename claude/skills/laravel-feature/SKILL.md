---
name: laravel-feature
description: Laravel feature scaffold — migration, model, controller, request, route, service, and test in the correct order
---

Use this skill when building a new Laravel feature from scratch.

## Step 0 — Check for Laravel Boost

Check if `laravel/boost` is in `composer.json`:

```bash
composer show laravel/boost 2>/dev/null
```

**If Boost is installed**, use its MCP tools throughout this skill:
- `Application Info` — verify PHP & Laravel version and installed packages before scaffolding
- `Database Schema` — read the actual schema before writing a migration (avoid redundant columns)
- `Search Docs` — query latest Laravel docs for the feature you're building
- `Last Error` / `Read Log Entries` — check for errors after each step
- `Database Query` — verify data looks correct after seeding or migrating

If Boost is not installed and the project is Laravel 12+, suggest:
```bash
composer require laravel/boost --dev
php artisan boost:install
```

---

## Step 1 — Clarify before scaffolding

Ask if not already clear:
- API only, or with Blade views?
- Resource controller (CRUD) or single-action?
- Does it need a Service layer (complex business logic) or is the controller enough?
- Any relationships to existing models?

## Step 2 — Scaffold in this order

### Migration + Model
```bash
php artisan make:model Foo -m
```
If Boost is available, read `Database Schema` first to understand existing tables and avoid redundant columns.

Edit the migration first — define all columns with correct types, nullable/default, and indexes before touching the model.

Model must define:
- `$fillable` (explicit, never `$guarded = []`)
- `$casts` for dates, booleans, JSON fields
- Relationships

### Form Request (validation)
```bash
php artisan make:request StoreFooRequest
php artisan make:request UpdateFooRequest
```
All validation lives here — not in the controller. `authorize()` returns `true` unless the feature has permission logic.

### Controller
```bash
php artisan make:controller FooController --resource --model=Foo
```

Keep controllers thin:
- Validate via Form Request (type-hint it)
- Delegate business logic to a Service
- Return API Resource or redirect

### API Resource (if API)
```bash
php artisan make:resource FooResource
php artisan make:resource FooCollection
```

### Service (if needed)
No artisan command — create manually at `app/Services/FooService.php`. Inject via constructor, bind in `AppServiceProvider` if needed.

### Route
```php
// api.php
Route::apiResource('foos', FooController::class);

// web.php
Route::resource('foos', FooController::class);
```

### Test
```bash
php artisan make:test FooTest --unit          # unit test for Service
php artisan make:test FooControllerTest       # feature test for HTTP layer
```

## Step 3 — Test structure

Feature tests must cover:
- Happy path (201/200 response, correct structure)
- Validation errors (422, field-level error messages)
- Auth/permission guard (401/403 if applicable)
- Edge cases (empty list, not found 404)

Use `RefreshDatabase` trait. Seed only what the test needs via factories.

## Step 4 — Checklist before PR

- [ ] Migration is reversible (`down()` method correct)
- [ ] No business logic in controller
- [ ] No raw queries unless justified — use Eloquent or Query Builder
- [ ] No N+1 — check with `->with()` on all eager-loadable relationships
- [ ] Validation covers all inputs — including types, max lengths, unique constraints
- [ ] Feature test covers happy path + at least one failure path
- [ ] `php artisan test` passes
- [ ] `php artisan route:list` shows the new route correctly
- [ ] If Boost installed: `Last Error` MCP tool shows no new errors after running tests

## Common patterns

```php
// Thin controller method
public function store(StoreFooRequest $request): FooResource
{
    $foo = $this->fooService->create($request->validated());
    return new FooResource($foo);
}

// Service
public function create(array $data): Foo
{
    return Foo::create($data);
}
```

```php
// Factory in test
$user = User::factory()->create();
$this->actingAs($user)->postJson('/api/foos', [...])->assertCreated();
```
