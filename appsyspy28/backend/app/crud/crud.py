from typing import List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

from app.models.models import (
    User, Class, ClassCategory, Room, Booking, Checkin,
    MemberCard, CardCategoryLink, CoachSchedule, PrivateBooking,
    PrivateCheckin, UserRole, BookingStatus, CheckinMethod, CardType
)
from app.schemas.schemas import (
    UserCreate, UserUpdate, ClassCreate, ClassUpdate,
    MemberCardCreate, MemberCardUpdate, BookingCreate,
    CoachScheduleCreate, PrivateBookingCreate
)
from app.core.security import get_password_hash

class UserCRUD:
    @staticmethod
    def create(db: Session, user_in: UserCreate) -> User:
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            username=user_in.username,
            password_hash=hashed_password,
            name=user_in.name,
            phone=user_in.phone,
            email=user_in.email,
            avatar=user_in.avatar,
            role=user_in.role,
            is_active=True
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_by_phone(db: Session, phone: str) -> Optional[User]:
        return db.query(User).filter(User.phone == phone).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def get_coaches(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).filter(
            User.role == UserRole.COACH,
            User.is_active == True
        ).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, db_user: User, user_in: UserUpdate) -> User:
        update_data = user_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def delete(db: Session, user_id: int) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_active = False
            db.commit()
            return True
        return False

class ClassCategoryCRUD:
    @staticmethod
    def create(db: Session, name: str, description: Optional[str] = None) -> ClassCategory:
        category = ClassCategory(name=name, description=description)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def get_by_id(db: Session, category_id: int) -> Optional[ClassCategory]:
        return db.query(ClassCategory).filter(ClassCategory.id == category_id).first()

    @staticmethod
    def get_all(db: Session, is_active: Optional[bool] = None) -> List[ClassCategory]:
        query = db.query(ClassCategory)
        if is_active is not None:
            query = query.filter(ClassCategory.is_active == is_active)
        return query.all()

class RoomCRUD:
    @staticmethod
    def create(db: Session, name: str, capacity: int, location: Optional[str] = None) -> Room:
        room = Room(name=name, capacity=capacity, location=location)
        db.add(room)
        db.commit()
        db.refresh(room)
        return room

    @staticmethod
    def get_by_id(db: Session, room_id: int) -> Optional[Room]:
        return db.query(Room).filter(Room.id == room_id).first()

    @staticmethod
    def get_by_qrcode(db: Session, qr_code: str) -> Optional[Room]:
        return db.query(Room).filter(Room.qr_code == qr_code).first()

    @staticmethod
    def get_all(db: Session, is_active: Optional[bool] = None) -> List[Room]:
        query = db.query(Room)
        if is_active is not None:
            query = query.filter(Room.is_active == is_active)
        return query.all()

class ClassCRUD:
    @staticmethod
    def create(db: Session, class_in: ClassCreate) -> Class:
        db_class = Class(
            category_id=class_in.category_id,
            coach_id=class_in.coach_id,
            room_id=class_in.room_id,
            name=class_in.name,
            description=class_in.description,
            class_date=class_in.class_date,
            start_time=class_in.start_time,
            end_time=class_in.end_time,
            capacity=class_in.capacity,
            is_active=class_in.is_active
        )
        db.add(db_class)
        db.commit()
        db.refresh(db_class)
        return db_class

    @staticmethod
    def get_by_id(db: Session, class_id: int) -> Optional[Class]:
        return db.query(Class).filter(Class.id == class_id).first()

    @staticmethod
    def get_by_id_with_details(db: Session, class_id: int) -> Optional[Class]:
        return db.query(Class).options(
            joinedload(Class.category),
            joinedload(Class.coach),
            joinedload(Class.room)
        ).filter(Class.id == class_id).first()

    @staticmethod
    def get_by_date_range(
        db: Session, 
        start_date: date, 
        end_date: date,
        category_id: Optional[int] = None,
        coach_id: Optional[int] = None,
        is_active: bool = True
    ) -> List[Class]:
        query = db.query(Class).options(
            joinedload(Class.category),
            joinedload(Class.coach),
            joinedload(Class.room)
        ).filter(
            Class.class_date >= start_date,
            Class.class_date <= end_date
        )
        if category_id:
            query = query.filter(Class.category_id == category_id)
        if coach_id:
            query = query.filter(Class.coach_id == coach_id)
        if is_active is not None:
            query = query.filter(Class.is_active == is_active)
        return query.order_by(Class.class_date, Class.start_time).all()

    @staticmethod
    def get_by_week(db: Session, week_start: date, week_end: date) -> List[Class]:
        return db.query(Class).options(
            joinedload(Class.category),
            joinedload(Class.coach),
            joinedload(Class.room)
        ).filter(
            Class.class_date >= week_start,
            Class.class_date <= week_end,
            Class.is_active == True
        ).order_by(Class.class_date, Class.start_time).all()

    @staticmethod
    def get_by_day(db: Session, class_date: date) -> List[Class]:
        return db.query(Class).options(
            joinedload(Class.category),
            joinedload(Class.coach),
            joinedload(Class.room)
        ).filter(
            Class.class_date == class_date,
            Class.is_active == True
        ).order_by(Class.start_time).all()

    @staticmethod
    def update(db: Session, db_class: Class, class_in: ClassUpdate) -> Class:
        update_data = class_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_class, key, value)
        db.commit()
        db.refresh(db_class)
        return db_class

    @staticmethod
    def increment_booked(db: Session, class_id: int) -> bool:
        db_class = db.query(Class).filter(Class.id == class_id).first()
        if db_class and db_class.booked_count < db_class.capacity:
            db_class.booked_count += 1
            db.commit()
            return True
        return False

    @staticmethod
    def decrement_booked(db: Session, class_id: int) -> bool:
        db_class = db.query(Class).filter(Class.id == class_id).first()
        if db_class and db_class.booked_count > 0:
            db_class.booked_count -= 1
            db.commit()
            return True
        return False

class MemberCardCRUD:
    @staticmethod
    def create(db: Session, card_in: MemberCardCreate) -> MemberCard:
        db_card = MemberCard(
            user_id=card_in.user_id,
            card_type=card_in.card_type,
            card_name=card_in.card_name,
            total_times=card_in.total_times,
            used_times=0,
            start_date=card_in.start_date,
            end_date=card_in.end_date,
            is_active=card_in.is_active
        )
        db.add(db_card)
        db.commit()
        db.refresh(db_card)
        
        for category_id in card_in.category_ids:
            link = CardCategoryLink(card_id=db_card.id, category_id=category_id)
            db.add(link)
        db.commit()
        db.refresh(db_card)
        return db_card

    @staticmethod
    def get_by_id(db: Session, card_id: int) -> Optional[MemberCard]:
        return db.query(MemberCard).options(
            joinedload(MemberCard.card_category_links).joinedload(CardCategoryLink.category)
        ).filter(MemberCard.id == card_id).first()

    @staticmethod
    def get_by_user(db: Session, user_id: int, is_active: Optional[bool] = None) -> List[MemberCard]:
        query = db.query(MemberCard).options(
            joinedload(MemberCard.card_category_links).joinedload(CardCategoryLink.category)
        ).filter(MemberCard.user_id == user_id)
        if is_active is not None:
            query = query.filter(MemberCard.is_active == is_active)
        return query.all()

    @staticmethod
    def get_active_valid_cards(
        db: Session, 
        user_id: int, 
        current_date: Optional[date] = None
    ) -> List[MemberCard]:
        if current_date is None:
            current_date = date.today()
        return db.query(MemberCard).options(
            joinedload(MemberCard.card_category_links).joinedload(CardCategoryLink.category)
        ).filter(
            MemberCard.user_id == user_id,
            MemberCard.is_active == True,
            MemberCard.start_date <= current_date,
            MemberCard.end_date >= current_date,
            or_(
                MemberCard.card_type != CardType.TIMES,
                and_(
                    MemberCard.card_type == CardType.TIMES,
                    MemberCard.used_times < MemberCard.total_times
                )
            )
        ).all()

    @staticmethod
    def can_use_for_category(
        db: Session, 
        card_id: int, 
        category_id: int
    ) -> bool:
        link = db.query(CardCategoryLink).filter(
            CardCategoryLink.card_id == card_id,
            CardCategoryLink.category_id == category_id
        ).first()
        return link is not None

    @staticmethod
    def use_card(db: Session, card_id: int) -> bool:
        card = db.query(MemberCard).filter(MemberCard.id == card_id).first()
        if not card:
            return False
        if card.card_type == CardType.TIMES:
            if card.used_times >= card.total_times:
                return False
            card.used_times += 1
        db.commit()
        return True

    @staticmethod
    def return_card(db: Session, card_id: int) -> bool:
        card = db.query(MemberCard).filter(MemberCard.id == card_id).first()
        if not card:
            return False
        if card.card_type == CardType.TIMES:
            if card.used_times > 0:
                card.used_times -= 1
        db.commit()
        return True

class BookingCRUD:
    @staticmethod
    def create(db: Session, booking_in: BookingCreate) -> Booking:
        db_booking = Booking(
            user_id=booking_in.user_id,
            class_id=booking_in.class_id,
            card_id=booking_in.card_id,
            status=BookingStatus.CONFIRMED
        )
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        return db_booking

    @staticmethod
    def get_by_id(db: Session, booking_id: int) -> Optional[Booking]:
        return db.query(Booking).filter(Booking.id == booking_id).first()

    @staticmethod
    def get_by_id_with_details(db: Session, booking_id: int) -> Optional[Booking]:
        return db.query(Booking).options(
            joinedload(Booking.class_).joinedload(Class.category),
            joinedload(Booking.class_).joinedload(Class.coach),
            joinedload(Booking.class_).joinedload(Class.room)
        ).filter(Booking.id == booking_id).first()

    @staticmethod
    def get_by_user(
        db: Session, 
        user_id: int, 
        status: Optional[BookingStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Booking]:
        query = db.query(Booking).options(
            joinedload(Booking.class_).joinedload(Class.category),
            joinedload(Booking.class_).joinedload(Class.coach),
            joinedload(Booking.class_).joinedload(Class.room)
        ).filter(Booking.user_id == user_id)
        if status:
            query = query.filter(Booking.status == status)
        return query.order_by(Booking.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_class(db: Session, class_id: int, status: Optional[BookingStatus] = None) -> List[Booking]:
        query = db.query(Booking).filter(Booking.class_id == class_id)
        if status:
            query = query.filter(Booking.status == status)
        return query.all()

    @staticmethod
    def get_by_user_and_class(db: Session, user_id: int, class_id: int) -> Optional[Booking]:
        return db.query(Booking).filter(
            Booking.user_id == user_id,
            Booking.class_id == class_id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
        ).first()

    @staticmethod
    def get_cancel_count_in_window(
        db: Session, 
        user_id: int, 
        start_date: date,
        end_date: date
    ) -> int:
        return db.query(Booking).filter(
            Booking.user_id == user_id,
            Booking.status == BookingStatus.CANCELLED,
            Booking.updated_at >= datetime.combine(start_date, datetime.min.time()),
            Booking.updated_at <= datetime.combine(end_date, datetime.max.time())
        ).count()

    @staticmethod
    def cancel(db: Session, booking_id: int, reason: Optional[str] = None) -> bool:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if booking and booking.status == BookingStatus.CONFIRMED:
            booking.status = BookingStatus.CANCELLED
            booking.cancel_reason = reason
            db.commit()
            return True
        return False

class CheckinCRUD:
    @staticmethod
    def create(
        db: Session, 
        user_id: int,
        booking_id: int,
        class_id: int,
        checkin_method: CheckinMethod,
        face_verified: bool = False
    ) -> Checkin:
        db_checkin = Checkin(
            user_id=user_id,
            booking_id=booking_id,
            class_id=class_id,
            checkin_method=checkin_method,
            checkin_time=datetime.utcnow(),
            face_verified=face_verified
        )
        db.add(db_checkin)
        
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if booking:
            booking.status = BookingStatus.COMPLETED
        
        db.commit()
        db.refresh(db_checkin)
        return db_checkin

    @staticmethod
    def get_by_booking(db: Session, booking_id: int) -> Optional[Checkin]:
        return db.query(Checkin).filter(Checkin.booking_id == booking_id).first()

    @staticmethod
    def get_by_user(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Checkin]:
        return db.query(Checkin).filter(
            Checkin.user_id == user_id
        ).order_by(Checkin.checkin_time.desc()).offset(skip).limit(limit).all()

class CoachScheduleCRUD:
    @staticmethod
    def create(db: Session, schedule_in: CoachScheduleCreate) -> CoachSchedule:
        db_schedule = CoachSchedule(
            coach_id=schedule_in.coach_id,
            schedule_date=schedule_in.schedule_date,
            start_time=schedule_in.start_time,
            end_time=schedule_in.end_time,
            is_available=schedule_in.is_available
        )
        db.add(db_schedule)
        db.commit()
        db.refresh(db_schedule)
        return db_schedule

    @staticmethod
    def get_by_id(db: Session, schedule_id: int) -> Optional[CoachSchedule]:
        return db.query(CoachSchedule).options(
            joinedload(CoachSchedule.coach)
        ).filter(CoachSchedule.id == schedule_id).first()

    @staticmethod
    def get_by_coach(
        db: Session, 
        coach_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        is_available: Optional[bool] = None
    ) -> List[CoachSchedule]:
        query = db.query(CoachSchedule).options(
            joinedload(CoachSchedule.coach)
        ).filter(CoachSchedule.coach_id == coach_id)
        
        if start_date:
            query = query.filter(CoachSchedule.schedule_date >= start_date)
        if end_date:
            query = query.filter(CoachSchedule.schedule_date <= end_date)
        if is_available is not None:
            query = query.filter(CoachSchedule.is_available == is_available)
        
        return query.order_by(CoachSchedule.schedule_date, CoachSchedule.start_time).all()

    @staticmethod
    def get_available_slots(
        db: Session,
        coach_id: int,
        start_date: Optional[date] = None
    ) -> List[CoachSchedule]:
        if start_date is None:
            start_date = date.today()
        return db.query(CoachSchedule).options(
            joinedload(CoachSchedule.coach)
        ).filter(
            CoachSchedule.coach_id == coach_id,
            CoachSchedule.schedule_date >= start_date,
            CoachSchedule.is_available == True,
            CoachSchedule.is_booked == False
        ).order_by(CoachSchedule.schedule_date, CoachSchedule.start_time).all()

    @staticmethod
    def book_slot(db: Session, schedule_id: int) -> bool:
        schedule = db.query(CoachSchedule).filter(
            CoachSchedule.id == schedule_id,
            CoachSchedule.is_available == True,
            CoachSchedule.is_booked == False
        ).first()
        if schedule:
            schedule.is_booked = True
            db.commit()
            return True
        return False

    @staticmethod
    def release_slot(db: Session, schedule_id: int) -> bool:
        schedule = db.query(CoachSchedule).filter(
            CoachSchedule.id == schedule_id
        ).first()
        if schedule:
            schedule.is_booked = False
            db.commit()
            return True
        return False

class PrivateBookingCRUD:
    @staticmethod
    def create(db: Session, member_id: int, booking_in: PrivateBookingCreate) -> PrivateBooking:
        db_booking = PrivateBooking(
            member_id=member_id,
            coach_id=booking_in.coach_id,
            schedule_id=booking_in.schedule_id,
            card_id=booking_in.card_id,
            status=BookingStatus.PENDING,
            class_name=booking_in.class_name,
            class_description=booking_in.class_description,
            location=booking_in.location,
            member_notes=booking_in.member_notes
        )
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        return db_booking

    @staticmethod
    def get_by_id(db: Session, booking_id: int) -> Optional[PrivateBooking]:
        return db.query(PrivateBooking).options(
            joinedload(PrivateBooking.member),
            joinedload(PrivateBooking.coach),
            joinedload(PrivateBooking.schedule)
        ).filter(PrivateBooking.id == booking_id).first()

    @staticmethod
    def get_by_member(
        db: Session, 
        member_id: int,
        status: Optional[BookingStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PrivateBooking]:
        query = db.query(PrivateBooking).options(
            joinedload(PrivateBooking.coach),
            joinedload(PrivateBooking.schedule)
        ).filter(PrivateBooking.member_id == member_id)
        if status:
            query = query.filter(PrivateBooking.status == status)
        return query.order_by(PrivateBooking.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_coach(
        db: Session, 
        coach_id: int,
        status: Optional[BookingStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PrivateBooking]:
        query = db.query(PrivateBooking).options(
            joinedload(PrivateBooking.member),
            joinedload(PrivateBooking.schedule)
        ).filter(PrivateBooking.coach_id == coach_id)
        if status:
            query = query.filter(PrivateBooking.status == status)
        return query.order_by(PrivateBooking.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def confirm(db: Session, booking_id: int, coach_notes: Optional[str] = None) -> bool:
        booking = db.query(PrivateBooking).filter(
            PrivateBooking.id == booking_id,
            PrivateBooking.status == BookingStatus.PENDING
        ).first()
        if booking:
            booking.status = BookingStatus.CONFIRMED
            if coach_notes:
                booking.coach_notes = coach_notes
            db.commit()
            return True
        return False

    @staticmethod
    def reject(db: Session, booking_id: int, cancel_reason: str) -> bool:
        booking = db.query(PrivateBooking).filter(
            PrivateBooking.id == booking_id,
            PrivateBooking.status == BookingStatus.PENDING
        ).first()
        if booking:
            booking.status = BookingStatus.CANCELLED
            booking.cancel_reason = cancel_reason
            CoachScheduleCRUD.release_slot(db, booking.schedule_id)
            db.commit()
            return True
        return False

    @staticmethod
    def cancel(db: Session, booking_id: int, cancel_reason: str) -> bool:
        booking = db.query(PrivateBooking).filter(
            PrivateBooking.id == booking_id,
            PrivateBooking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
        ).first()
        if booking:
            booking.status = BookingStatus.CANCELLED
            booking.cancel_reason = cancel_reason
            CoachScheduleCRUD.release_slot(db, booking.schedule_id)
            db.commit()
            return True
        return False

class PrivateCheckinCRUD:
    @staticmethod
    def create(
        db: Session, 
        user_id: int,
        private_booking_id: int,
        checkin_method: CheckinMethod,
        face_verified: bool = False
    ) -> PrivateCheckin:
        db_checkin = PrivateCheckin(
            user_id=user_id,
            private_booking_id=private_booking_id,
            checkin_method=checkin_method,
            checkin_time=datetime.utcnow(),
            face_verified=face_verified
        )
        db.add(db_checkin)
        
        booking = db.query(PrivateBooking).filter(PrivateBooking.id == private_booking_id).first()
        if booking:
            booking.status = BookingStatus.COMPLETED
        
        db.commit()
        db.refresh(db_checkin)
        return db_checkin

    @staticmethod
    def get_by_booking(db: Session, private_booking_id: int) -> Optional[PrivateCheckin]:
        return db.query(PrivateCheckin).filter(
            PrivateCheckin.private_booking_id == private_booking_id
        ).first()

user_crud = UserCRUD()
category_crud = ClassCategoryCRUD()
room_crud = RoomCRUD()
class_crud = ClassCRUD()
card_crud = MemberCardCRUD()
booking_crud = BookingCRUD()
checkin_crud = CheckinCRUD()
coach_schedule_crud = CoachScheduleCRUD()
private_booking_crud = PrivateBookingCRUD()
private_checkin_crud = PrivateCheckinCRUD()
