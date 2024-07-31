package actas

import (
	"fmt"
	"log/slog"
	"time"
)

func retry[T any](f func() (*T, error), n int, delayMillis int) (*T, error) {
	attempts := 0
	for {
		t, e := f()
		if e != nil {
			if attempts < n {
				attempts++
				slog.Info(fmt.Sprintf("failed on attempt %d. sleeping and retrying", attempts))
				time.Sleep(time.Duration(delayMillis) * time.Millisecond)
				continue
			} else {
				return nil, e
			}
		}
		return t, nil
	}
}
