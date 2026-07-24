// frontend/__tests__/index.test.tsx 

import { describe, it, expect } from 'vitest' // 1. Must be first
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import Home from '../src/app/page.tsx'

describe('Automated Homepage Render Test', () => {
    it('renders the system dashboard heading without crashing', () => {
        render(<Home />)
        const heading = screen.getByRole('heading', {
            name: /production dashboard/i,
        })

        expect(heading).toBeInTheDocument()
    })
})