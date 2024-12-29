export enum DayOfWeek {
    Monday = "Monday",
    Tuesday = "Tuesday",
    Wednesday = "Wednesday",
    Thursday = "Thursday",
    Friday = "Friday",
    Saturday = "Saturday",
    Sunday = "Sunday"
}

export class Shift {
    id: string
    series: string
    day_of_week: DayOfWeek
    start_time: string
    end_time: string
    required_tas: number
    // Optional
    alias: string = "DEFAULT"
    shift_date: Date = new Date(1900, 1, 1)

    constructor(id: string, series: string, day_of_week: DayOfWeek, start_time: string, end_time: string, required_tas: number, alias: string = "DEFAULT", shift_date: Date = new Date(1900, 1, 1)) {
        this.id = id
        this.series = series
        this.day_of_week = day_of_week
        this.start_time = start_time
        this.end_time = end_time
        this.required_tas = required_tas
        this.alias = alias
        this.shift_date = shift_date
    }
}

export class TA {
    id: string
    name: string
    required_shifts: number
    desired: Shift[] = []
    undesired: Shift[] = []
    unavailable: Shift[] = []
    // favourite_partners: TA[] = None
    is_grad_student: boolean = true

    constructor(id: string, name: string, required_shifts: number, desired: Shift[] = [], undesired: Shift[] = [], unavailable: Shift[] = [], is_grad_student: boolean = true) {
        this.id = id
        this.name = name
        this.required_shifts = required_shifts
        this.desired = desired
        this.undesired = undesired
        this.unavailable = unavailable
        this.is_grad_student = is_grad_student
    }

    get_status_for_shift(shift: Shift): string {
        if (this.desired.includes(shift))
            return 'Desired'
        if (this.undesired.includes(shift))
            return 'Undesired'
        if (this.unavailable.includes(shift))
            return 'Unavailable'
        return 'Neutral'
    }

    is_available_for_shift(shift: Shift): boolean {
        return !this.unavailable.includes(shift)
    }
}

export class ShiftAssignment {
    id: string
    assigned_ta?: TA
    shift: Shift

    constructor(id: string, shift: Shift, assigned_ta?: TA) {
        this.id = id
        this.assigned_ta = assigned_ta
        this.shift = shift
    }
}

export class Score {
    hardScore: number
    softScore: number
    initScore: number

    constructor(hardScore: number = 0, softScore: number = 0, initScore: number = 0) {
        this.hardScore = hardScore
        this.softScore = softScore
        this.initScore = initScore
    }
}

export class Timetable {
    id: string
    // problem facts
    shifts: Shift[]
    tas: TA[]
    // planning entities
    shift_assignments: ShiftAssignment[]
    score: Score

    constructor(id: string, shifts: Shift[], tas: TA[], shift_assignments: ShiftAssignment[], score: Score = new Score()) {
        this.id = id
        this.shifts = shifts
        this.tas = tas
        this.shift_assignments = shift_assignments
        this.score = score
    }
}
