package domain

import "context"

type DispatchRepository interface {
	Save(ctx context.Context, dispatch *Dispatch) error
	FindByID(ctx context.Context, id string) (*Dispatch, error)
}
